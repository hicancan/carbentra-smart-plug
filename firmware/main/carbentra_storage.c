#include "carbentra_storage.h"
#include "carbentra_storage_contract.h"
#include "nvs_flash.h"
/* All failures are fail-closed. In particular ESP_ERR_NVS_NO_FREE_PAGES and
 * NEW_VERSION_FOUND must not trigger the common destructive erase-and-retry. */
esp_err_t carbentra_storage_boot(nvs_handle_t *journal,uint64_t *last_seq,uint64_t *boots){
 if(!journal||!last_seq||!boots)return ESP_ERR_INVALID_ARG;
 *last_seq=0;*boots=0;
 esp_err_t e=nvs_flash_init();if(e!=ESP_OK)return e;
 e=nvs_open(CARBENTRA_NVS_JOURNAL,NVS_READWRITE,journal);if(e!=ESP_OK)return e;
 e=nvs_get_u64(*journal,"last_seq",last_seq);if(e!=ESP_OK&&e!=ESP_ERR_NVS_NOT_FOUND)goto fail;
 e=nvs_get_u64(*journal,"boots",boots);if(e!=ESP_OK&&e!=ESP_ERR_NVS_NOT_FOUND)goto fail;
 if(*boots==UINT64_MAX){e=ESP_ERR_INVALID_STATE;goto fail;}
 ++*boots;
 e=nvs_set_u64(*journal,"boots",*boots);if(e!=ESP_OK)goto fail;
 e=nvs_commit(*journal);if(e!=ESP_OK)goto fail;
 return ESP_OK;
fail:
 nvs_close(*journal);*journal=0;return e;
}
