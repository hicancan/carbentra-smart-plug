#include "cm_network.h"
#include "cm_command_json.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <math.h>
#include <errno.h>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_random.h"
#include "nvs.h"
#include "mqtt_client.h"
#include "cJSON.h"
#include "wifi_provisioning/manager.h"
#include "wifi_provisioning/scheme_ble.h"
#include "esp_sntp.h"
#define MAX_COMMAND 1024
static const char *TAG="cm_network";
static esp_mqtt_client_handle_t client;
static QueueHandle_t commands,receipts;
typedef struct {cm_command command;uint32_t received_epoch;} queued_command;
typedef struct {char epoch[33];uint64_t sequence;} receipt;
static volatile bool connected;
static unsigned dropped;
static char command_topic[96], time_topic[96], receipt_topic[96], base_topic[80];
static char clock_nonce[33];
static bool clock_trusted; static int64_t clock_anchor_lower_s,clock_anchor_upper_s;static uint32_t network_epoch; static uint64_t clock_anchor_ms,clock_requested_ms;
static int rx_kind;
static portMUX_TYPE clock_mux=portMUX_INITIALIZER_UNLOCKED;
static char *broker_uri,*ca_pem,*client_pem,*client_key;
static char rx[MAX_COMMAND+1];static size_t rx_len,rx_total;
static bool accepting;
static uint8_t salt[64],verifier[512];
static wifi_prov_security2_params_t sec2;
static esp_timer_handle_t provision_timeout,reconnect_timer;
static unsigned reconnect_s=1;
static char *read_string(nvs_handle_t h,const char *key,size_t maximum){
 size_t n=0;if(nvs_get_str(h,key,NULL,&n)!=ESP_OK||n<2||n>maximum)return NULL;
 char *p=calloc(1,n);if(!p)return NULL;
 if(nvs_get_str(h,key,p,&n)!=ESP_OK){free(p);return NULL;}return p;
}
static void request_clock(void){
 uint32_t n[4];esp_fill_random(n,sizeof(n));
 char nonce[33];snprintf(nonce,sizeof(nonce),"%08"PRIx32"%08"PRIx32"%08"PRIx32"%08"PRIx32,n[0],n[1],n[2],n[3]);
 portENTER_CRITICAL(&clock_mux);memcpy(clock_nonce,nonce,sizeof(nonce));clock_requested_ms=esp_timer_get_time()/1000;portEXIT_CRITICAL(&clock_mux);
 char text[96];snprintf(text,sizeof(text),"{\"clock_nonce\":\"%s\"}",nonce);
 cm_network_publish("hello",text);
}
static void receive_receipt(const char*text){
 cJSON*j=cJSON_ParseWithLengthOpts(text,strlen(text)+1,NULL,true);if(!j)return;
 cJSON*e=cJSON_GetObjectItemCaseSensitive(j,"boot_epoch"),*s=cJSON_GetObjectItemCaseSensitive(j,"sample_seq");
 if(cJSON_IsString(e)&&e->valuestring&&strlen(e->valuestring)==32&&cJSON_IsString(s)&&s->valuestring&&strlen(s->valuestring)>0&&strlen(s->valuestring)<=20){
  bool ok=true;for(const char*p=s->valuestring;*p;p++)if(*p<'0'||*p>'9')ok=false;
  errno=0;receipt r={0};char*end;r.sequence=strtoull(s->valuestring,&end,10);if(errno||*end||r.sequence==0)ok=false;
  memcpy(r.epoch,e->valuestring,32);if(ok)xQueueSend(receipts,&r,0);
 }
 cJSON_Delete(j);
}
static void receive_clock(const char *text){
 cJSON*j=cJSON_ParseWithLengthOpts(text,strlen(text)+1,NULL,true);if(!j)return;
 cJSON*n=cJSON_GetObjectItemCaseSensitive(j,"clock_nonce"),*t=cJSON_GetObjectItemCaseSensitive(j,"unix_s");
 uint64_t now=esp_timer_get_time()/1000;char expected[33];uint64_t requested;
 portENTER_CRITICAL(&clock_mux);memcpy(expected,clock_nonce,sizeof(expected));requested=clock_requested_ms;portEXIT_CRITICAL(&clock_mux);
 if(cJSON_IsString(n)&&n->valuestring&&!strcmp(n->valuestring,expected)&&cJSON_IsNumber(t)&&isfinite(t->valuedouble)&&floor(t->valuedouble)==t->valuedouble&&t->valuedouble>=1700000000&&t->valuedouble<4102444800.0&&now>=requested&&now-requested<=2000){
  portENTER_CRITICAL(&clock_mux);clock_anchor_lower_s=(int64_t)t->valuedouble;clock_anchor_upper_s=(int64_t)t->valuedouble+1+(int64_t)((now-requested+999)/1000);clock_anchor_ms=now;clock_trusted=true;portEXIT_CRITICAL(&clock_mux);
 }
 cJSON_Delete(j);
}
static void mqtt_event(void *arg,esp_event_base_t base,int32_t id,void *data){
 (void)arg;(void)base;esp_mqtt_event_handle_t e=data;
 if(id==MQTT_EVENT_CONNECTED){connected=true;portENTER_CRITICAL(&clock_mux);network_epoch++;clock_trusted=false;portEXIT_CRITICAL(&clock_mux);esp_mqtt_client_subscribe(client,command_topic,1);esp_mqtt_client_subscribe(client,time_topic,1);esp_mqtt_client_subscribe(client,receipt_topic,1);request_clock();}
 else if(id==MQTT_EVENT_DISCONNECTED){connected=false;accepting=false;portENTER_CRITICAL(&clock_mux);clock_trusted=false;portEXIT_CRITICAL(&clock_mux);if(commands)xQueueReset(commands);}
 else if(id==MQTT_EVENT_DATA){
  if(e->current_data_offset==0){rx_len=0;rx_total=e->total_data_len;
   rx_kind=0;
   if(e->topic&&e->topic_len==(int)strlen(command_topic)&&memcmp(e->topic,command_topic,e->topic_len)==0)rx_kind=1;
   else if(e->topic&&e->topic_len==(int)strlen(time_topic)&&memcmp(e->topic,time_topic,e->topic_len)==0)rx_kind=2;
   else if(e->topic&&e->topic_len==(int)strlen(receipt_topic)&&memcmp(e->topic,receipt_topic,e->topic_len)==0)rx_kind=3;
   accepting=!e->retain&&rx_total>0&&rx_total<=MAX_COMMAND&&rx_kind!=0;}
  if(!accepting)return;
  if(e->current_data_offset!=(int)rx_len||e->data_len<0||rx_len+(size_t)e->data_len>rx_total){accepting=false;dropped++;return;}
  memcpy(rx+rx_len,e->data,e->data_len);rx_len+=e->data_len;
  if(rx_len==rx_total){rx[rx_len]=0;queued_command c={.received_epoch=cm_network_epoch()};
   if(memchr(rx,0,rx_len)){dropped++;}
   else if(rx_kind==2)receive_clock(rx);
   else if(rx_kind==3)receive_receipt(rx);
   else if(!cm_parse_command(rx,&c.command)||xQueueSend(commands,&c,0)!=pdTRUE)dropped++;
   accepting=false;}
 }
}
static void reconnect(void*arg){(void)arg;esp_wifi_connect();}
static void stop_provisioning(void*arg){(void)arg;wifi_prov_mgr_stop_provisioning();}
static void wifi_event(void*arg,esp_event_base_t base,int32_t id,void*data){
 (void)arg;(void)data;
 if(base==WIFI_EVENT&&id==WIFI_EVENT_STA_START)esp_wifi_connect();
 if(base==WIFI_EVENT&&id==WIFI_EVENT_STA_DISCONNECTED){connected=false;
  if(reconnect_timer){esp_timer_stop(reconnect_timer);esp_timer_start_once(reconnect_timer,(uint64_t)reconnect_s*1000000);if(reconnect_s<32)reconnect_s*=2;}}
 if(base==IP_EVENT&&id==IP_EVENT_STA_GOT_IP){reconnect_s=1;
  static bool started;if(client&&!started){esp_mqtt_client_start(client);started=true;}
  #if defined(CONFIG_CM_SNTP_SERVER)
  if(strlen(CONFIG_CM_SNTP_SERVER)>0&&!esp_sntp_enabled()) {esp_sntp_setoperatingmode(SNTP_OPMODE_POLL);esp_sntp_setservername(0,CONFIG_CM_SNTP_SERVER);esp_sntp_init();}
  #endif
 }
 if(base==WIFI_PROV_EVENT&&id==WIFI_PROV_END){if(provision_timeout)esp_timer_stop(provision_timeout);wifi_prov_mgr_deinit();}
}
esp_err_t cm_network_start(const char*device_id){
 /* Credentials are provisioned by the owner outside this source project.
    Never ship common passwords, private keys or Security0 provisioning. */
 nvs_handle_t n;esp_err_t err=nvs_open("cm_secure",NVS_READONLY,&n);
 if(err!=ESP_OK){ESP_LOGW(TAG,"No owner provisioning: networking stays disabled");return err;}
 broker_uri=read_string(n,"broker",256);ca_pem=read_string(n,"ca_pem",8192);
 client_pem=read_string(n,"client_cert",8192);client_key=read_string(n,"client_key",8192);
 if(!broker_uri||strncmp(broker_uri,"mqtts://",8)||!ca_pem||!client_pem||!client_key){nvs_close(n);ESP_LOGE(TAG,"mTLS configuration incomplete; no insecure fallback");return ESP_ERR_INVALID_STATE;}
 snprintf(base_topic,sizeof(base_topic),"carbonmirror/v1/%s",device_id);
 snprintf(command_topic,sizeof(command_topic),"%s/cmd",base_topic);snprintf(time_topic,sizeof(time_topic),"%s/time",base_topic);snprintf(receipt_topic,sizeof(receipt_topic),"%s/receipt",base_topic);
 commands=xQueueCreate(8,sizeof(queued_command));receipts=xQueueCreate(8,sizeof(receipt));if(!commands||!receipts){nvs_close(n);return ESP_ERR_NO_MEM;}
 esp_mqtt_client_config_t cfg={.broker.address.uri=broker_uri,.broker.verification.certificate=ca_pem,
 .credentials.client_id=device_id,.credentials.authentication.certificate=client_pem,.credentials.authentication.key=client_key,
 .session.keepalive=30,.buffer.size=2048,.outbox.limit=32768,.network.reconnect_timeout_ms=10000,.network.timeout_ms=10000};
 client=esp_mqtt_client_init(&cfg);if(!client){nvs_close(n);return ESP_FAIL;}
 ESP_ERROR_CHECK(esp_mqtt_client_register_event(client,ESP_EVENT_ANY_ID,mqtt_event,NULL));
 ESP_ERROR_CHECK(esp_netif_init());ESP_ERROR_CHECK(esp_event_loop_create_default());esp_netif_create_default_wifi_sta();
 wifi_init_config_t w=WIFI_INIT_CONFIG_DEFAULT();ESP_ERROR_CHECK(esp_wifi_init(&w));
 ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT,ESP_EVENT_ANY_ID,wifi_event,NULL));
 ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT,IP_EVENT_STA_GOT_IP,wifi_event,NULL));
 ESP_ERROR_CHECK(esp_event_handler_register(WIFI_PROV_EVENT,ESP_EVENT_ANY_ID,wifi_event,NULL));
 esp_timer_create_args_t rt={.callback=reconnect,.name="wifi_retry"};ESP_ERROR_CHECK(esp_timer_create(&rt,&reconnect_timer));
 wifi_prov_mgr_config_t pc={.scheme=wifi_prov_scheme_ble,.scheme_event_handler=WIFI_PROV_SCHEME_BLE_EVENT_HANDLER_FREE_BTDM};
 ESP_ERROR_CHECK(wifi_prov_mgr_init(pc));bool provisioned=false;ESP_ERROR_CHECK(wifi_prov_mgr_is_provisioned(&provisioned));
 if(provisioned){wifi_prov_mgr_deinit();ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));err=esp_wifi_start();}
 else {
  size_t sl=sizeof(salt),vl=sizeof(verifier);uint8_t permit=0;
  if(nvs_get_blob(n,"srp_salt",salt,&sl)!=ESP_OK||nvs_get_blob(n,"srp_verifier",verifier,&vl)!=ESP_OK||nvs_get_u8(n,"prov_allow",&permit)!=ESP_OK||!permit||sl<16||vl!=384){wifi_prov_mgr_deinit();err=ESP_ERR_INVALID_STATE;}
  else {sec2.salt=(const char*)salt;sec2.salt_len=sl;sec2.verifier=(const char*)verifier;sec2.verifier_len=vl;
   err=wifi_prov_mgr_start_provisioning(WIFI_PROV_SECURITY_2,&sec2,device_id,NULL);
   if(err==ESP_OK){esp_timer_create_args_t pt={.callback=stop_provisioning,.name="prov_limit"};ESP_ERROR_CHECK(esp_timer_create(&pt,&provision_timeout));esp_timer_start_once(provision_timeout,180ULL*1000000);}}
 }
 nvs_close(n);return err;
}
bool cm_network_online(void){return connected;}
bool cm_network_command(cm_command*out,uint32_t*received_epoch){queued_command q;if(!commands||!out||!received_epoch||xQueueReceive(commands,&q,0)!=pdTRUE)return false;*out=q.command;*received_epoch=q.received_epoch;return true;}
int cm_network_publish(const char*kind,const char*json){if(!connected||!client)return -1;char topic[110];snprintf(topic,sizeof(topic),"%s/%s",base_topic,kind);return esp_mqtt_client_enqueue(client,topic,json,0,1,0,true);}
unsigned cm_network_dropped_commands(void){return dropped;}

void cm_network_tick(void){uint64_t now=esp_timer_get_time()/1000;portENTER_CRITICAL(&clock_mux);bool need=(!clock_trusted||now-clock_anchor_ms>300000)&&now-clock_requested_ms>15000;portEXIT_CRITICAL(&clock_mux);if(connected&&need)request_clock();}
bool cm_network_trusted_time(int64_t*lower,int64_t*upper){
 uint64_t now=esp_timer_get_time()/1000;portENTER_CRITICAL(&clock_mux);
 bool ok=clock_trusted&&now>=clock_anchor_ms&&now-clock_anchor_ms<=600000;
 int64_t elapsed=ok?(int64_t)((now-clock_anchor_ms)/1000):0;
 int64_t lo=clock_anchor_lower_s+(elapsed>0?elapsed-1:0),hi=clock_anchor_upper_s+elapsed+1;
 portEXIT_CRITICAL(&clock_mux);
 if(ok){if(lower)*lower=lo;if(upper)*upper=hi;}return ok;
}
uint32_t cm_network_epoch(void){portENTER_CRITICAL(&clock_mux);uint32_t e=network_epoch;portEXIT_CRITICAL(&clock_mux);return e;}

bool cm_network_receipt(char epoch[33],uint64_t*seq){receipt r;if(!receipts||xQueueReceive(receipts,&r,0)!=pdTRUE)return false;memcpy(epoch,r.epoch,33);*seq=r.sequence;return true;}
