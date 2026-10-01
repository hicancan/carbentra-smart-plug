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
#include "carbentra_storage.h"
#include "carbentra_storage_contract.h"
#include "carbentra_execution.h"
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
static carbentra_execution execution;
static unsigned dropped_telemetry;
static char boot_epoch[33];
static uint64_t last_sample_send_ms;
static carbentra_button local_button;
static uint64_t local_event_seq,local_event_ms;
static carbentra_result local_event_result=CARBENTRA_INVALID;
static double energy_forward_wh,energy_reverse_wh;static unsigned energy_gaps;
typedef struct {carbentra_measurement m;int64_t lower_s,upper_s;uint64_t monotonic_ms;bool time_trusted,fault_latched,desired_on,output_present,feedback_valid;uint64_t seq,local_event_seq,local_event_ms,manual_hold_until_ms;carbentra_result local_event_result;const char *control_mode;bool commissioned,maintenance;carbentra_feedback_status feedback_status;bool calibrated;double forward_wh,reverse_wh;unsigned energy_gaps,ram_dropped,command_dropped;} sample;
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
static bool request_relay(bool on){
 #if CONFIG_CARBENTRA_ALLOW_ACTUATION
 if(on&&!state.commissioned)return false;
 return gpio_set_level(RELAY_GPIO,on?1:0)==ESP_OK;
 #else
 gpio_set_level(RELAY_GPIO,0);return !on;
 #endif
}
static bool save_sequence(uint64_t seq){return journal_ready&&nvs_set_u64(journal,"last_seq",seq)==ESP_OK&&nvs_commit(journal)==ESP_OK;}
static bool acknowledge(const carbentra_command*c,const char*status,const carbentra_execution*result){
 if(!carbentra_network_online())return false;
 cJSON*j=cJSON_CreateObject();if(!j)return false;char seq[24];snprintf(seq,sizeof(seq),"%"PRIu64,c->seq);
 cJSON_AddNumberToObject(j,"schema_version",CARBENTRA_WIRE_VERSION);
 cJSON_AddStringToObject(j,"device_id",state.device_id);cJSON_AddStringToObject(j,"boot_epoch",boot_epoch);
 cJSON_AddStringToObject(j,"id",c->id);cJSON_AddStringToObject(j,"seq",seq);cJSON_AddStringToObject(j,"status",status);
 bool terminal=result?result->status!=CARBENTRA_EXEC_WAITING:true;
 cJSON_AddBoolToObject(j,"terminal",terminal);
 cJSON_AddBoolToObject(j,"desired_on",result&&terminal?result->desired_on:state.desired_on);
 cJSON_AddBoolToObject(j,"fault_latched",result&&terminal?result->fault_latched:state.fault_latched);
 cJSON_AddBoolToObject(j,"voltage_absence_proven",false);
 if(result){
  cJSON_AddNumberToObject(j,"requested_monotonic_ms",(double)result->requested_ms);
  cJSON_AddNumberToObject(j,"deadline_monotonic_ms",(double)result->deadline_ms);
  if(terminal){
   cJSON_AddNumberToObject(j,"observed_monotonic_ms",(double)result->observed_ms);
   cJSON_AddBoolToObject(j,"feedback_valid",result->feedback_valid);cJSON_AddBoolToObject(j,"output_present",result->output_present);
   cJSON_AddStringToObject(j,"output_sensing",carbentra_feedback_name(result->sensing));
  }
 }
 char*text=cJSON_PrintUnformatted(j);bool ok=text&&carbentra_network_publish("ack",text)>=0;
 if(text){cJSON_free(text);}
 cJSON_Delete(j);return ok;
}
static void load_profile(void){nvs_handle_t n;if(nvs_open(CARBENTRA_NVS_FACTORY,NVS_READONLY,&n)!=ESP_OK)return;
 size_t len=sizeof(profile.id);uint8_t approved=0,critical=1,shed=0,commissioned=0;
 if(nvs_get_str(n,"profile_id",profile.id,&len)!=ESP_OK)strcpy(profile.id,"unknown");
 uint8_t maintenance=0;esp_err_t maintenance_status=nvs_get_u8(n,"maintenance",&maintenance);state.maintenance=maintenance!=0||(maintenance_status!=ESP_OK&&maintenance_status!=ESP_ERR_NVS_NOT_FOUND);
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
static void sample_append(uint64_t now){
 if(sample_seq==UINT64_MAX){state.commissioned=false;return;}
 if(count==BUFFER_CAP){head=(head+1)%BUFFER_CAP;count--;dropped_telemetry++;}
 carbentra_feedback_status captured_feedback=feedback_status(now);
 sample s={.local_event_seq=local_event_seq,.local_event_ms=local_event_ms,.local_event_result=local_event_result,.manual_hold_until_ms=state.manual_hold_until_ms,.control_mode=carbentra_control_mode(&state,&profile,now),.commissioned=state.commissioned,.maintenance=state.maintenance,.m=measurement,.monotonic_ms=now,.fault_latched=state.fault_latched,.desired_on=state.desired_on,.output_present=captured_feedback==CARBENTRA_FB_AC_PRESENT,.seq=++sample_seq,.feedback_status=captured_feedback,.calibrated=carbentra_meter_calibrated(),.forward_wh=energy_forward_wh,.reverse_wh=energy_reverse_wh,.energy_gaps=energy_gaps,.ram_dropped=dropped_telemetry,.command_dropped=carbentra_network_dropped_commands()};s.feedback_valid=captured_feedback==CARBENTRA_FB_AC_PRESENT||captured_feedback==CARBENTRA_FB_NO_AC_PULSES;
 s.time_trusted=carbentra_network_trusted_time_at(now,&s.lower_s,&s.upper_s);
 buffer[(head+count)%BUFFER_CAP]=s;count++;
}
static void sample_flush(void){
 char epoch[33];uint64_t seq;
 while(carbentra_network_receipt(epoch,&seq)){if(count&&!strcmp(epoch,boot_epoch)&&buffer[head].seq==seq){head=(head+1)%BUFFER_CAP;count--;last_sample_send_ms=0;}}
 if(!count||!carbentra_network_online())return;
 uint64_t now=esp_timer_get_time()/1000;if(last_sample_send_ms&&now-last_sample_send_ms<3000)return;
 sample*s=&buffer[head];
 cJSON*j=cJSON_CreateObject();char seq_text[24];snprintf(seq_text,sizeof(seq_text),"%"PRIu64,s->seq);
 cJSON_AddStringToObject(j,"device_id",state.device_id);cJSON_AddStringToObject(j,"boot_epoch",boot_epoch);cJSON_AddStringToObject(j,"sample_seq",seq_text);cJSON_AddStringToObject(j,"board_revision",CARBENTRA_BOARD_REVISION);cJSON_AddNumberToObject(j,"schema_version",CARBENTRA_WIRE_VERSION);
 cJSON_AddBoolToObject(j,"calibrated",s->calibrated);cJSON_AddBoolToObject(j,"valid",s->m.valid);
 cJSON_AddNumberToObject(j,"monotonic_ms",(double)s->monotonic_ms);cJSON_AddNumberToObject(j,"measurement_monotonic_ms",(double)s->m.sampled_ms);
 cJSON_AddStringToObject(j,"time_quality",s->time_trusted?"authenticated":"unknown");
 if(s->time_trusted){cJSON_AddNumberToObject(j,"unix_s",(double)(s->lower_s+(s->upper_s-s->lower_s)/2));cJSON_AddNumberToObject(j,"unix_lower_s",(double)s->lower_s);cJSON_AddNumberToObject(j,"unix_upper_s",(double)s->upper_s);}
 else{cJSON_AddNullToObject(j,"unix_s");cJSON_AddNullToObject(j,"unix_lower_s");cJSON_AddNullToObject(j,"unix_upper_s");}
 cJSON_AddBoolToObject(j,"fault_latched",s->fault_latched);
 cJSON_AddStringToObject(j,"device_type","smart_plug");cJSON_AddStringToObject(j,"channel_id","relay.1");
 cJSON_AddStringToObject(j,"control_mode",s->control_mode);cJSON_AddBoolToObject(j,"actuation_enabled",s->commissioned);cJSON_AddBoolToObject(j,"maintenance",s->maintenance);
 char local_seq_text[24],local_ms_text[24],hold_text[24];snprintf(local_seq_text,sizeof(local_seq_text),"%"PRIu64,s->local_event_seq);snprintf(local_ms_text,sizeof(local_ms_text),"%"PRIu64,s->local_event_ms);snprintf(hold_text,sizeof(hold_text),"%"PRIu64,s->manual_hold_until_ms);
 cJSON_AddStringToObject(j,"manual_hold_until_uptime_ms",hold_text);
 cJSON *local=cJSON_AddObjectToObject(j,"last_local_input");cJSON_AddNumberToObject(local,"channel",1);cJSON_AddStringToObject(local,"event_seq",local_seq_text);cJSON_AddStringToObject(local,"uptime_ms",local_ms_text);cJSON_AddBoolToObject(local,"pressed",s->local_event_seq!=0);cJSON_AddStringToObject(local,"result",s->local_event_seq?carbentra_result_name(s->local_event_result):"none");
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
 uint8_t mac[6];ESP_ERROR_CHECK(esp_read_mac(mac,ESP_MAC_WIFI_STA));snprintf(state.device_id,sizeof(state.device_id),"CM-%02X%02X%02X%02X%02X%02X",mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]);
 uint64_t boots=0;
 journal_ready=carbentra_storage_boot(&journal,&state.last_seq,&boots)==ESP_OK;
 if(!journal_ready)ESP_LOGE(TAG,"NVS journal unavailable; no erase, commissioning or networking");
 snprintf(boot_epoch,sizeof(boot_epoch),"%016"PRIx64"%02x%02x%02x%02x%02x%02x0000",boots,mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]);
 esp_err_t meter_status=carbentra_meter_start();ESP_LOGI(TAG,"Meter startup status: %s",esp_err_to_name(meter_status));load_profile();
 if(!journal_ready)state.commissioned=false;
 if(journal_ready)carbentra_network_start(state.device_id);else ESP_LOGE(TAG,"Journal unavailable; networking disabled");
 uint64_t sample_at=0,publish_at=0,mismatch_since=0;
 carbentra_command pending={0};bool pending_valid=false;uint64_t pending_since=0;uint32_t pending_epoch=0;
 while(1){uint64_t now=esp_timer_get_time()/1000;
  if(now-sample_at>=1000){carbentra_meter_sample(&measurement);
   if(measurement.energy_forward_valid)energy_forward_wh+=measurement.energy_forward_counts*(double)measurement.energy_wh_per_count;
   if(measurement.energy_reverse_valid)energy_reverse_wh+=measurement.energy_reverse_counts*(double)measurement.energy_wh_per_count;
   if(measurement.energy_uncertain||!measurement.valid)energy_gaps++;
   sample_at=now;}
  carbentra_feedback_status fb=feedback_status(now);
  bool feedback_valid=fb==CARBENTRA_FB_AC_PRESENT||fb==CARBENTRA_FB_NO_AC_PULSES;
  bool actual=fb==CARBENTRA_FB_AC_PRESENT;
  bool settled=now>=state.changed_ms&&now-state.changed_ms>=100;
  bool bad=settled&&(fb==CARBENTRA_FB_PRESENT_OR_STUCK_LOW||fb==CARBENTRA_FB_UNKNOWN||(state.desired_on&&!actual)||(!state.desired_on&&actual));
  if(bad){if(!mismatch_since)mismatch_since=now;}else mismatch_since=0;
  bool trip=settled&&(fb==CARBENTRA_FB_PRESENT_OR_STUCK_LOW||(mismatch_since&&now-mismatch_since>1000));
  carbentra_network_tick();int64_t lower=0,upper=0;bool clock_ok=carbentra_network_trusted_time(&lower,&upper);
  /* A new request must not hide an unsettled output mismatch before the
     local latch qualifies. Feedback validity alone is insufficient. */
  carbentra_context x={.online=carbentra_network_online(),.authenticated=carbentra_network_online(),.authorized=true,.clock_trusted=clock_ok,
   .observation_valid=measurement.valid&&feedback_valid&&!bad,.local_trip=trip,.wall_lower_s=lower,.wall_upper_s=upper,.mono_ms=now,.sampled_ms=measurement.sampled_ms};
  /* Authorization derives from mutually authenticated, exact per-device topic
     plus locally commissioned profile; broker ACL deployment remains mandatory. */
  if(carbentra_button_press(&local_button,!gpio_get_level(BUTTON_GPIO),now)){
   carbentra_decision d=carbentra_evaluate_local(&state,&profile,!state.desired_on,&x);
   if(local_event_seq!=UINT64_MAX)local_event_seq++;
   local_event_ms=now;
   if(d.actuate&&!request_relay(d.target_on)){d.status=CARBENTRA_INVALID;d.actuate=false;}
   carbentra_commit_local(&state,&x,d);local_event_result=d.status;sample_append(now);
  }
  carbentra_decision local=carbentra_evaluate(&state,&profile,NULL,&x);
  if(local.latch_fault){bool new_fault=!state.fault_latched;request_relay(false);carbentra_commit(&state,NULL,&x,local);if(new_fault)sample_append(now);}
  carbentra_execution_poll(&execution,now,state.desired_on,state.fault_latched,fb);
  if(execution.needs_publish&&acknowledge(&execution.command,carbentra_execution_name(execution.status),&execution))execution.needs_publish=false;
  if(pending_valid&&(!carbentra_network_online()||pending_epoch!=carbentra_network_epoch()))pending_valid=false;
  if(!pending_valid&&carbentra_network_command(&pending,&pending_epoch)){pending_valid=true;pending_since=now;}
  if(pending_valid&&(!carbentra_network_online()||pending_epoch!=carbentra_network_epoch()))pending_valid=false;
  if(pending_valid){
   carbentra_command command=pending;
   carbentra_decision d=carbentra_evaluate(&state,&profile,&command,&x);
   bool wait_for_lower=d.status==CARBENTRA_BAD_WINDOW&&clock_ok&&command.issued_s>lower&&command.issued_s<=upper&&command.expires_s>upper&&now-pending_since<5000;
   if(wait_for_lower){vTaskDelay(pdMS_TO_TICKS(20));continue;}
   pending_valid=false;
   if(d.status==CARBENTRA_DUPLICATE&&execution.status!=CARBENTRA_EXEC_IDLE&&execution.command.seq==command.seq&&!strcmp(execution.command.id,command.id)){
    acknowledge(&command,carbentra_execution_name(execution.status),&execution);
   }else if(d.status==CARBENTRA_ACCEPTED){
    if(execution.status==CARBENTRA_EXEC_WAITING||execution.needs_publish){acknowledge(&command,"BUSY_AWAITING_FEEDBACK",NULL);}
    else
    if(now-last_accepted_ms<1000){acknowledge(&command,"RATE_LIMIT",NULL);}
    else if(!save_sequence(command.seq)){state.commissioned=false;acknowledge(&command,"PERSISTENCE_FAILURE",NULL);}
    else {
     /* Consume sequence even if physical request fails; retries cannot energize. */
     state.last_seq=command.seq;last_accepted_ms=now;
     if(!carbentra_network_online()||pending_epoch!=carbentra_network_epoch()){acknowledge(&command,"SESSION_CHANGED",NULL);}
     else if(d.actuate&&!request_relay(d.target_on)){acknowledge(&command,"ACTUATION_DISABLED_OR_FAILED",NULL);}
     else{carbentra_commit(&state,&command,&x,d);carbentra_execution_begin(&execution,&command,state.desired_on,now);acknowledge(&command,d.actuate?"REQUESTED_AWAITING_FEEDBACK":"ACCEPTED_NO_CHANGE",&execution);}
    }
   }else acknowledge(&command,carbentra_result_name(d.status),NULL);
  }
  if(now-publish_at>=5000){sample_append(now);publish_at=now;}
  sample_flush();gpio_set_level(LED_GPIO,state.fault_latched?((now/200)%2):carbentra_network_online());
  vTaskDelay(pdMS_TO_TICKS(50));
 }
}
