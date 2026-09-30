#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
typedef struct {
 bool valid; uint64_t sampled_ms; float volts,amps,watts,vars,va,hz,pf,board_c;
 bool board_temperature_valid; uint16_t system_status;
 bool energy_forward_valid,energy_reverse_valid,energy_uncertain;
 uint16_t energy_forward_counts,energy_reverse_counts;
 float energy_wh_per_count; uint64_t energy_interval_ms;
} cm_measurement;
esp_err_t cm_meter_start(void);
esp_err_t cm_meter_sample(cm_measurement*);
bool cm_meter_calibrated(void);
