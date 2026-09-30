#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"
#include "carbentra_policy.h"
esp_err_t carbentra_network_start(const char *device_id);
bool carbentra_network_online(void);
bool carbentra_network_command(carbentra_command *out,uint32_t *received_epoch);
int carbentra_network_publish(const char *kind,const char *json);
unsigned carbentra_network_dropped_commands(void);

void carbentra_network_tick(void);
bool carbentra_network_trusted_time(int64_t *lower_s,int64_t *upper_s);

bool carbentra_network_receipt(char epoch[33],uint64_t *sequence);

uint32_t carbentra_network_epoch(void);
