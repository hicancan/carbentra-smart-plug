#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"
#include "cm_policy.h"
esp_err_t cm_network_start(const char *device_id);
bool cm_network_online(void);
bool cm_network_command(cm_command *out,uint32_t *received_epoch);
int cm_network_publish(const char *kind,const char *json);
unsigned cm_network_dropped_commands(void);

void cm_network_tick(void);
bool cm_network_trusted_time(int64_t *lower_s,int64_t *upper_s);

bool cm_network_receipt(char epoch[33],uint64_t *sequence);

uint32_t cm_network_epoch(void);
