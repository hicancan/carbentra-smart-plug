#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
uint16_t cm_meter_checksum(const uint16_t *registers,size_t count);
float cm_meter_power_factor(uint16_t raw);
float cm_meter_signed_power(uint16_t raw);
uint32_t cm_crc32(const void *data,size_t length);

bool cm_meter_run_state_ok(uint16_t cal_start,uint16_t adj_start,uint16_t cs1,uint16_t cs2,uint16_t expected1,uint16_t expected2,uint16_t status);
