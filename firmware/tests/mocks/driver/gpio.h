#pragma once
#include <stdint.h>
#include "esp_err.h"
typedef struct {uint64_t pin_bit_mask;int mode,pull_up_en;} gpio_config_t;
#define GPIO_MODE_OUTPUT 1
#define GPIO_MODE_INPUT 2
#define GPIO_PULLUP_ENABLE 1
#define GPIO_INTR_ANYEDGE 1
esp_err_t gpio_config(const gpio_config_t*);
esp_err_t gpio_set_level(int,unsigned);
int gpio_get_level(int);
esp_err_t gpio_install_isr_service(int);
esp_err_t gpio_set_intr_type(int,int);
esp_err_t gpio_isr_handler_add(int,void(*)(void*),void*);
