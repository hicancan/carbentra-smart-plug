#pragma once
#include <stdint.h>
#include "esp_err.h"
#include "nvs.h"
esp_err_t carbentra_storage_boot(nvs_handle_t *journal, uint64_t *last_seq, uint64_t *boot_count);
