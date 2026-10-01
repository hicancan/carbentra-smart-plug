#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define CARBENTRA_CALIBRATION_VERSION 3
/* Explicit little-endian packed storage wire format, ESP32-C3 is little endian. */
#if defined(_MSC_VER)
#pragma pack(push, 1)
typedef struct {
#else
typedef struct __attribute__((packed)) {
#endif
 uint32_t magic,version; char board_revision[24],calibration_id[32];
 uint16_t calibration[11],adjustment[10];float meter_constant_pulses_per_kwh;uint32_t crc;
} carbentra_calibration_record;
#if defined(_MSC_VER)
#pragma pack(pop)
#endif
_Static_assert(sizeof(carbentra_calibration_record)==114,"Calibration storage ABI changed");
bool carbentra_calibration_valid(const void *data,size_t size);
