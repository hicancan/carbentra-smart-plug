#include "carbentra_storage.h"
#include "carbentra_storage_contract.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int fail_at,step,closed,missing;static uint64_t old_seq=42,old_boots=7,saved;
static int operation(void){return ++step==fail_at?ESP_FAIL:ESP_OK;}
esp_err_t nvs_flash_init(void){return operation();}
esp_err_t nvs_open(const char*n,int mode,nvs_handle_t*h){assert(strlen(n)<=15);assert(!strcmp(n,CARBENTRA_NVS_JOURNAL));assert(mode==NVS_READWRITE);*h=9;return operation();}
esp_err_t nvs_get_u64(nvs_handle_t h,const char*k,uint64_t*v){assert(h==9);int e=operation();if(e)return e;if(missing)return ESP_ERR_NVS_NOT_FOUND;*v=!strcmp(k,"last_seq")?old_seq:old_boots;return 0;}
esp_err_t nvs_set_u64(nvs_handle_t h,const char*k,uint64_t v){assert(h==9&&!strcmp(k,"boots"));saved=v;return operation();}
esp_err_t nvs_commit(nvs_handle_t h){assert(h==9);return operation();}
void nvs_close(nvs_handle_t h){assert(h==9);closed++;}
int main(void){nvs_handle_t h=0;uint64_t seq=0,boots=0;
 assert(carbentra_storage_boot(NULL,&seq,&boots)==ESP_ERR_INVALID_ARG);
 for(fail_at=1;fail_at<=6;fail_at++){step=closed=0;assert(carbentra_storage_boot(&h,&seq,&boots)!=ESP_OK);assert(closed==(fail_at>=3));}
 fail_at=step=closed=0;assert(carbentra_storage_boot(&h,&seq,&boots)==ESP_OK);assert(seq==42&&boots==8&&saved==8&&!closed);
 missing=1;step=0;assert(carbentra_storage_boot(&h,&seq,&boots)==ESP_OK);assert(seq==0&&boots==1);
 missing=0;old_boots=UINT64_MAX;step=0;assert(carbentra_storage_boot(&h,&seq,&boots)==ESP_ERR_INVALID_STATE);assert(step==4&&h==0);
 puts("PASS NVS startup: stable namespaces, replay preservation, six injected errors, fresh store and boot overflow; no erase API");return 0;}
