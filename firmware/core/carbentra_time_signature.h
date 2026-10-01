#pragma once
#include <stdbool.h>
#include <stdint.h>
bool carbentra_verify_time_response(const char *json,const char *nonce,const char *public_pem,uint64_t elapsed_ms,int64_t *unix_s);
