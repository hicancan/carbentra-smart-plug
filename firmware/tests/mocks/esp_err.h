#pragma once
#include <assert.h>
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_INVALID_ARG 1
#define ESP_ERR_INVALID_STATE 2
#define ESP_ERR_NVS_NOT_FOUND 3
#define ESP_ERR_NO_MEM 4
#define ESP_ERR_INVALID_RESPONSE 5
#define ESP_ERROR_CHECK(e) assert((e)==ESP_OK)
static inline const char *esp_err_to_name(esp_err_t e){(void)e;return "mock";}
