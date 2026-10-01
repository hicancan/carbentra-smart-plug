#define CONFIG_CARBENTRA_BOARD_REV_B 1
#define CONFIG_CARBENTRA_ALLOW_ACTUATION 0
#include <assert.h>
#include <setjmp.h>
#include <stdlib.h>
#include "../main/app_main.c"
static bool mutate_feedback_on_timer;
static bool transport_online;static char published[4096],published_kind[32];
static jmp_buf stop;static uint64_t mock_ms;static int failure,operation_count,network_starts,relay_high,delays;
static int operation(void){return ++operation_count==failure?ESP_FAIL:ESP_OK;}
esp_err_t nvs_flash_init(void){return operation();}
esp_err_t nvs_open(const char*n,int mode,nvs_handle_t*h){assert(strlen(n)<=15);if(mode==NVS_READONLY)return ESP_ERR_NVS_NOT_FOUND;assert(!strcmp(n,CARBENTRA_NVS_JOURNAL));*h=1;return operation();}
esp_err_t nvs_get_u64(nvs_handle_t h,const char*k,uint64_t*v){(void)h;int e=operation();if(e)return e;*v=!strcmp(k,"last_seq")?42:7;return ESP_OK;}
esp_err_t nvs_set_u64(nvs_handle_t h,const char*k,uint64_t v){(void)h;(void)k;(void)v;return operation();}
esp_err_t nvs_commit(nvs_handle_t h){(void)h;return operation();}
void nvs_close(nvs_handle_t h){(void)h;}
esp_err_t nvs_get_u8(nvs_handle_t h,const char*k,uint8_t*v){(void)h;(void)k;(void)v;return ESP_ERR_NVS_NOT_FOUND;}
esp_err_t nvs_get_u32(nvs_handle_t h,const char*k,uint32_t*v){(void)h;(void)k;(void)v;return ESP_ERR_NVS_NOT_FOUND;}
esp_err_t nvs_get_str(nvs_handle_t h,const char*k,char*v,size_t*n){(void)h;(void)k;(void)v;(void)n;return ESP_ERR_NVS_NOT_FOUND;}
esp_err_t gpio_config(const gpio_config_t*g){(void)g;return ESP_OK;}
esp_err_t gpio_set_level(int pin,unsigned level){if(pin==RELAY_GPIO&&level)relay_high++;return ESP_OK;}
int gpio_get_level(int pin){(void)pin;return 1;}
esp_err_t gpio_install_isr_service(int flags){(void)flags;return ESP_OK;}
esp_err_t gpio_set_intr_type(int pin,int type){(void)pin;(void)type;return ESP_OK;}
esp_err_t gpio_isr_handler_add(int pin,void(*cb)(void*),void*a){(void)pin;(void)cb;(void)a;return ESP_OK;}
esp_err_t esp_read_mac(uint8_t*mac,int type){(void)type;for(int i=0;i<6;i++)mac[i]=(uint8_t)(i*0x11);return ESP_OK;}
int64_t esp_timer_get_time(void){if(mutate_feedback_on_timer){feedback_state.initialized=false;mutate_feedback_on_timer=false;}return (int64_t)mock_ms*1000;}
void vTaskDelay(unsigned ms){mock_ms+=ms;if(++delays==150)longjmp(stop,1);}
esp_err_t carbentra_meter_start(void){return ESP_ERR_INVALID_STATE;}
bool carbentra_meter_calibrated(void){return false;}
esp_err_t carbentra_meter_sample(carbentra_measurement*m){memset(m,0,sizeof(*m));m->sampled_ms=mock_ms;m->energy_uncertain=true;return ESP_ERR_INVALID_STATE;}
esp_err_t carbentra_network_start(const char*id){assert(!strcmp(id,"CM-001122334455"));network_starts++;return ESP_ERR_INVALID_STATE;}
bool carbentra_network_online(void){return transport_online;}
bool carbentra_network_command(carbentra_command*c,uint32_t*e){(void)c;(void)e;return false;}
int carbentra_network_publish(const char*k,const char*j){snprintf(published,sizeof(published),"%s",j);snprintf(published_kind,sizeof(published_kind),"%s",k);return transport_online?1:-1;}
unsigned carbentra_network_dropped_commands(void){return 0;}
void carbentra_network_tick(void){}
bool carbentra_network_trusted_time(int64_t*l,int64_t*u){(void)l;(void)u;return false;}
bool carbentra_network_trusted_time_at(uint64_t n,int64_t*l,int64_t*u){(void)n;(void)l;(void)u;return false;}
bool carbentra_network_receipt(char e[33],uint64_t*s){(void)e;(void)s;return false;}
uint32_t carbentra_network_epoch(void){return 0;}
int main(int argc,char**argv){
 failure=argc>1?atoi(argv[1]):0;if(!setjmp(stop))app_main();
 assert(!relay_high&&!state.commissioned);assert(network_starts==(failure==0));assert(count>=1);assert(buffer[head].time_trusted==false&&!buffer[head].m.valid);assert(!request_relay(true));assert(!relay_high);
 /* Simulate an ISR changing feedback between two possible classifications.
    The telemetry booleans and label must all come from one captured state. */
 carbentra_feedback_state prior_feedback=feedback_state;size_t prior_count=count;uint64_t prior_seq=sample_seq;
 feedback_state=(carbentra_feedback_state){.initialized=true,.level=true,.good_periods=3,.last_good_us=mock_ms*1000-10000,.last_edge_us=mock_ms*1000-10000};
 mutate_feedback_on_timer=true;sample_append(mock_ms);sample *captured=&buffer[(head+count-1)%BUFFER_CAP];
 assert(captured->feedback_status==CARBENTRA_FB_AC_PRESENT&&captured->feedback_valid&&captured->output_present);
 feedback_state=prior_feedback;count=prior_count;sample_seq=prior_seq;
 if(getenv("CARBENTRA_DUMP_WIRE")){
  transport_online=true;sample_flush();assert(!strcmp(published_kind,"telemetry"));printf("WIRE %s\n",published);
  sample*s=&buffer[head];s->seq=2;s->calibrated=s->m.valid=s->time_trusted=true;s->lower_s=1800000000;s->upper_s=1800000004;s->m.volts=230;s->m.amps=0.5;s->m.watts=100;s->m.vars=0;s->m.va=115;s->m.pf=0.87;s->m.hz=50;s->m.board_temperature_valid=true;s->m.board_c=23;s->forward_wh=12.5;s->reverse_wh=0.1;last_sample_send_ms=0;sample_flush();printf("WIRE %s\n",published);
  carbentra_command c={.id="synthetic-hold-001",.seq=1};carbentra_execution_begin(&execution,&c,false,10000);acknowledge(&c,"ACCEPTED_NO_CHANGE",&execution);printf("ACK %s\n",published);
  assert(carbentra_execution_poll(&execution,10100,false,false,CARBENTRA_FB_NO_AC_PULSES));acknowledge(&c,carbentra_execution_name(execution.status),&execution);printf("ACK %s\n",published);
 }
 printf("PASS app_main mocked startup failure=%d: relay off, invalid measurements explicit, journal failure blocks networking; coherent ISR feedback snapshot\n",failure);return 0;}
