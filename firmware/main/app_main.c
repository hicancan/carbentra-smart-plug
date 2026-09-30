#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <time.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "cJSON.h"
#include "carbentra_policy.h"
#include "carbentra_network.h"
#include "carbentra_meter.h"
#include "carbentra_meter_decode.h"
#include "carbentra_feedback.h"
#if !CONFIG_CARBENTRA_BOARD_REV_B
#error "This firmware supports only the reviewed Rev B pin contract"
#endif
#define RELAY_GPIO 10
#define BUTTON_GPIO 18
#define LED_GPIO 19
#define FEEDBACK_GPIO 3
#define BUFFER_CAP 64
static carbentra_state state;
static carbentra_profile profile={.id="unknown",.min_on_ms=300000,.min_off_ms=300000};
static carbentra_measurement measurement;
static carbentra_feedback_state feedback_state;
static portMUX_TYPE feedback_mux=portMUX_INITIALIZER_UNLOCKED;
static const char*TAG="carbentra_endpoint";
static nvs_handle_t journal;
static bool journal_ready;
static uint64_t last_accepted_ms;
static unsigned dropped_telemetry;
static char boot_epoch[33];
static uint64_t last_sample_send_ms;
static double energy_forward_wh,energy_reverse_wh;static unsigned energy_gaps;
typedef struct {carbentra_measurement m;int64_t unix_s;bool desired_on,output_present,feedback_valid;uint64_t seq;carbentra_feedback_status feedback_status;bool calibrated;double forward_wh,reverse_wh;unsigned energy_gaps,ram_dropped,command_dropped;} sample;
static sample buffer[BUFFER_CAP];static size_t head,count;static uint64_t sample_seq;
static void feedback_edge(void*arg){
 (void)arg;uint64_t now=esp_timer_get_time();bool level=gpio_get_level(FEEDBACK_GPIO);
 portENTER_CRITICAL_ISR(&feedback_mux);carbentra_feedback_edge(&feedback_state,now,level);portEXIT_CRITICAL_ISR(&feedback_mux);
}
static carbentra_feedback_status feedback_status(uint64_t unused_ms){
 (void)unused_ms;
 portENTER_CRITICAL(&feedback_mux);carbentra_feedback_state snapshot=feedback_state;portEXIT_CRITICAL(&feedback_mux);
 return carbentra_feedback_classify(&snapshot,esp_timer_get_time());
}
static bool feedback_present(uint64_t now,bool*valid){
 carbentra_feedback_status status=feedback_status(now);
 *valid=status==CARBENTRA_FB_AC_PRESENT||status==CARBENTRA_FB_NO_AC_PULSES;
 return status==CARBENTRA_FB_AC_PRESENT;
}
static bool request_relay(bool on){
 #if CONFIG_CARBENTRA_ALLOW_ACTUATION
 if(on&&!state.commissioned)return false;
 return gpio_set_level(RELAY_GPIO,on?1:0)==ESP_OK;
 #else
 gpio_set_level(RELAY_GPIO,0);return !on;
 #endif
}
static bool save_sequence(uint64_t seq){return journal_ready&&nvs_set_u64(journal,"last_seq",seq)==ESP_OK&&nvs_commit(journal)==ESP_OK;}
static void acknowledge(const carbentra_command*c,const char*status){
 cJSON*j=cJSON_CreateObject();cJSON_AddStringToObject(j,"id",c->id);cJSON_AddStringToObject(j,"status",status);cJSON_AddBoolToObject(j,"desired_on",state.desired_on);cJSON_AddBoolToObject(j,"fault_latched",state.fault_latched);
 char*s=cJSON_PrintUnformatted(j);if(s){carbentra_network_publish("ack",s);cJSON_free(s);}cJSON_Delete(j);
}
static void load_profile(void){nvs_handle_t n;if(nvs_open("carbentra_factory",NVS_READONLY,&n)!=ESP_OK)return;
 size_t len=sizeof(profile.id);uint8_t approved=0,critical=1,shed=0,commissioned=0;
 if(nvs_get_str(n,"profile_id",profile.id,&len)!=ESP_OK)strcpy(profile.id,"unknown");
 nvs_get_u8(n,"approved",&approved);nvs_get_u8(n,"critical",&critical);nvs_get_u8(n,"allow_shed",&shed);nvs_get_u8(n,"commissioned",&commissioned);
 nvs_get_u32(n,"min_on_ms",&profile.min_on_ms);nvs_get_u32(n,"min_off_ms",&profile.min_off_ms);
 profile.approved=approved==1;profile.critical=critical!=0;profile.allow_mains_shed=shed==1;
 /* Physical release must be represented by deliberate per-unit commissioning,
    never inferred from compilation or presence of a network credential. */
 #if CONFIG_CARBENTRA_ALLOW_ACTUATION
 state.commissioned=commissioned==1&&profile.approved&&carbentra_meter_calibrated();
 #else
 state.commissioned=false;(void)commissioned;
 #endif
 nvs_close(n);
}
static void sample_append(uint64_t now){bool valid;sample s={.m=measurement,.unix_s=time(NULL),.desired_on=state.desired_on,.output_present=feedback_present(now,&valid),.seq=++sample_seq,.feedback_status=feedback_status(now),.calibrated=carbentra_meter_calibrated(),.forward_wh=energy_forward_wh,.reverse_wh=energy_reverse_wh,.energy_gaps=energy_gaps,.ram_dropped=dropped_telemetry,.command_dropped=carbentra_network_dropped_commands()};s.feedback_valid=valid;
 if(count==BUFFER_CAP){head=(head+1)%BUFFER_CAP;count--;dropped_telemetry++;}
 buffer[(head+count)%BUFFER_CAP]=s;count++;
}
static void sample_flush(void){
 char epoch[33];uint64_t seq;
 while(carbentra_network_receipt(epoch,&seq)){if(count&&!strcmp(epoch,boot_epoch)&&buffer[head].seq==seq){head=(head+1)%BUFFER_CAP;count--;last_sample_send_ms=0;}}
 if(!count||!carbentra_network_online())return;
 uint64_t now=esp_timer_get_time()/1000;if(last_sample_send_ms&&now-last_sample_send_ms<3000)return;
 sample*s=&buffer[head];
 cJSON*j=cJSON_CreateObject();char seq_text[24];snprintf(seq_text,sizeof(seq_text),"%"PRIu64,s->seq);
 cJSON_AddStringToObject(j,"device_id",state.device_id);cJSON_AddStringToObject(j,"boot_epoch",boot_epoch);cJSON_AddStringToObject(j,"sample_seq",seq_text);cJSON_AddStringToObject(j,"board_revision","CARBENTRA-P16-EVT-B");
 cJSON_AddBoolToObject(j,"calibrated",s->calibrated);cJSON_AddBoolToObject(j,"valid",s->m.valid);
 cJSON_AddNumberToObject(j,"monotonic_ms",(double)s->m.sampled_ms);cJSON_AddNumberToObject(j,"unix_s",(double)s->unix_s);cJSON_AddBoolToObject(j,"clock_plausible",s->unix_s>=1700000000);
 if(s->m.valid){cJSON_AddNumberToObject(j,"voltage_v",s->m.volts);cJSON_AddNumberToObject(j,"current_a",s->m.amps);cJSON_AddNumberToObject(j,"active_w",s->m.watts);cJSON_AddNumberToObject(j,"reactive_var",s->m.vars);cJSON_AddNumberToObject(j,"apparent_va",s->m.va);cJSON_AddNumberToObject(j,"pf",s->m.pf);cJSON_AddNumberToObject(j,"frequency_hz",s->m.hz);}
 cJSON_AddBoolToObject(j,"board_temperature_valid",s->m.board_temperature_valid);if(s->m.board_temperature_valid)cJSON_AddNumberToObject(j,"board_temperature_c",s->m.board_c);
 cJSON_AddBoolToObject(j,"desired_on",s->desired_on);cJSON_AddBoolToObject(j,"feedback_valid",s->feedback_valid);cJSON_AddBoolToObject(j,"output_present",s->output_present);cJSON_AddStringToObject(j,"output_sensing",carbentra_feedback_name(s->feedback_status));cJSON_AddBoolToObject(j,"voltage_absence_proven",false);
 cJSON_AddNumberToObject(j,"ram_buffer_dropped",s->ram_dropped);cJSON_AddNumberToObject(j,"command_dropped",s->command_dropped);
 cJSON_AddStringToObject(j,"energy_status",s->calibrated?"calibrated_counts_known_intervals_since_boot_not_billing_certified":"uncalibrated_no_energy_result");
 cJSON_AddNumberToObject(j,"known_forward_wh_since_boot",s->forward_wh);cJSON_AddNumberToObject(j,"known_reverse_wh_since_boot",s->reverse_wh);cJSON_AddNumberToObject(j,"energy_uncertain_intervals",s->energy_gaps);
 char*text=cJSON_PrintUnformatted(j);if(text){if(carbentra_network_publish("telemetry",text)>=0){last_sample_send_ms=now;}cJSON_free(text);}cJSON_Delete(j);
 /* Remove only after matching durable edge receipt; retries preserve epoch/sequence. RAM is not power-loss storage. */
}
void app_main(void){
 gpio_config_t out={.pin_bit_mask=(1ULL<<RELAY_GPIO)|(1ULL<<LED_GPIO),.mode=GPIO_MODE_OUTPUT};ESP_ERROR_CHECK(gpio_config(&out));gpio_set_level(RELAY_GPIO,0);gpio_set_level(LED_GPIO,0);
 gpio_config_t inputs={.pin_bit_mask=(1ULL<<BUTTON_GPIO)|(1ULL<<FEEDBACK_GPIO),.mode=GPIO_MODE_INPUT,.pull_up_en=GPIO_PULLUP_ENABLE};ESP_ERROR_CHECK(gpio_config(&inputs));
 carbentra_feedback_init(&feedback_state,esp_timer_get_time(),gpio_get_level(FEEDBACK_GPIO));
 ESP_ERROR_CHECK(gpio_install_isr_service(0));ESP_ERROR_CHECK(gpio_set_intr_type(FEEDBACK_GPIO,GPIO_INTR_ANYEDGE));ESP_ERROR_CHECK(gpio_isr_handler_add(FEEDBACK_GPIO,feedback_edge,NULL));
 esp_err_t nvs=nvs_flash_init();if(nvs!=ESP_OK){ESP_LOGE(TAG,"NVS unavailable; refusing erase or operation");return;}
 uint8_t mac[6];ESP_ERROR_CHECK(esp_read_mac(mac,ESP_MAC_WIFI_STA));snprintf(state.device_id,sizeof(state.device_id),"CM-%02X%02X%02X%02X%02X%02X",mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]);
 journal_ready=nvs_open("carbentra_journal",NVS_READWRITE,&journal)==ESP_OK;
 uint64_t boots=0;
 if(journal_ready){esp_err_t e=nvs_get_u64(journal,"last_seq",&state.last_seq);if(e!=ESP_OK&&e!=ESP_ERR_NVS_NOT_FOUND)journal_ready=false;
  e=nvs_get_u64(journal,"boots",&boots);if(e!=ESP_OK&&e!=ESP_ERR_NVS_NOT_FOUND)journal_ready=false;
  if(boots==UINT64_MAX)journal_ready=false;else boots++;
  if(journal_ready&&(nvs_set_u64(journal,"boots",boots)!=ESP_OK||nvs_commit(journal)!=ESP_OK))journal_ready=false;
 }
 snprintf(boot_epoch,sizeof(boot_epoch),"%016"PRIx64"%02x%02x%02x%02x%02x%02x0000",boots,mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]);
 esp_err_t meter_status=carbentra_meter_start();ESP_LOGI(TAG,"Meter startup status: %s",esp_err_to_name(meter_status));load_profile();
 if(!journal_ready)state.commissioned=false;
 if(journal_ready)carbentra_network_start(state.device_id);else ESP_LOGE(TAG,"Journal unavailable; networking disabled");
 uint64_t sample_at=0,publish_at=0,button_since=0,mismatch_since=0;
 carbentra_command pending={0};bool pending_valid=false;uint64_t pending_since=0;uint32_t pending_epoch=0;
 while(1){uint64_t now=esp_timer_get_time()/1000;
  if(now-sample_at>=1000){carbentra_meter_sample(&measurement);
   if(measurement.energy_forward_valid)energy_forward_wh+=measurement.energy_forward_counts*(double)measurement.energy_wh_per_count;
   if(measurement.energy_reverse_valid)energy_reverse_wh+=measurement.energy_reverse_counts*(double)measurement.energy_wh_per_count;
   if(measurement.energy_uncertain||!measurement.valid)energy_gaps++;
   sample_at=now;}
  bool feedback_valid;bool actual=feedback_present(now,&feedback_valid);
  carbentra_feedback_status fb=feedback_status(now);
  bool settled=now>=state.changed_ms&&now-state.changed_ms>=100;
  bool bad=settled&&(fb==CARBENTRA_FB_PRESENT_OR_STUCK_LOW||fb==CARBENTRA_FB_UNKNOWN||(state.desired_on&&!actual)||(!state.desired_on&&actual));
  if(bad){if(!mismatch_since)mismatch_since=now;}else mismatch_since=0;
  bool trip=settled&&(fb==CARBENTRA_FB_PRESENT_OR_STUCK_LOW||(mismatch_since&&now-mismatch_since>1000));
  /* Local button only requests OFF, never blindly toggles unknown loads ON. */
  if(!gpio_get_level(BUTTON_GPIO)){if(!button_since)button_since=now;if(now-button_since>=100&&state.desired_on){request_relay(false);state.desired_on=false;state.changed_ms=now;}}
  else button_since=0;
  carbentra_network_tick();int64_t lower=0,upper=0;bool clock_ok=carbentra_network_trusted_time(&lower,&upper);
  carbentra_context x={.online=carbentra_network_online(),.authenticated=carbentra_network_online(),.authorized=true,.clock_trusted=clock_ok,
   .observation_valid=measurement.valid&&feedback_valid,.local_trip=trip,.wall_lower_s=lower,.wall_upper_s=upper,.mono_ms=now,.sampled_ms=measurement.sampled_ms};
  /* Authorization derives from mutually authenticated, exact per-device topic
     plus locally commissioned profile; broker ACL deployment remains mandatory. */
  carbentra_decision local=carbentra_evaluate(&state,&profile,NULL,&x);
  if(local.latch_fault){request_relay(false);carbentra_commit(&state,NULL,&x,local);}
  if(pending_valid&&(!carbentra_network_online()||pending_epoch!=carbentra_network_epoch()))pending_valid=false;
  if(!pending_valid&&carbentra_network_command(&pending,&pending_epoch)){pending_valid=true;pending_since=now;}
  if(pending_valid&&(!carbentra_network_online()||pending_epoch!=carbentra_network_epoch()))pending_valid=false;
  if(pending_valid){
   carbentra_command command=pending;
   carbentra_decision d=carbentra_evaluate(&state,&profile,&command,&x);
   bool wait_for_lower=d.status==CARBENTRA_BAD_WINDOW&&clock_ok&&command.issued_s>lower&&command.issued_s<=upper&&command.expires_s>upper&&now-pending_since<5000;
   if(wait_for_lower){vTaskDelay(pdMS_TO_TICKS(20));continue;}
   pending_valid=false;
   if(d.status==CARBENTRA_ACCEPTED){
    if(now-last_accepted_ms<1000){acknowledge(&command,"RATE_LIMIT");}
    else if(!save_sequence(command.seq)){state.commissioned=false;acknowledge(&command,"PERSISTENCE_FAILURE");}
    else {
     /* Consume sequence even if physical request fails; retries cannot energize. */
     state.last_seq=command.seq;last_accepted_ms=now;
     if(!carbentra_network_online()||pending_epoch!=carbentra_network_epoch()){acknowledge(&command,"SESSION_CHANGED");}
     else if(d.actuate&&!request_relay(d.target_on)){acknowledge(&command,"ACTUATION_DISABLED_OR_FAILED");}
     else{carbentra_commit(&state,&command,&x,d);acknowledge(&command,d.actuate?"REQUESTED_AWAITING_FEEDBACK":"ACCEPTED_NO_CHANGE");}
    }
   }else acknowledge(&command,carbentra_result_name(d.status));
  }
  if(now-publish_at>=5000){sample_append(now);publish_at=now;}
  sample_flush();gpio_set_level(LED_GPIO,state.fault_latched?((now/200)%2):carbentra_network_online());
  vTaskDelay(pdMS_TO_TICKS(50));
 }
}
