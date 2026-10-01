#pragma once
#include <stddef.h>
#include "cJSON.h"
/* Caller owns returned object. Reject ambiguous duplicate keys, escaped NUL,
 * excessive nesting and unexpected envelope field count before consuming it. */
cJSON *carbentra_json_object(const char *text,size_t maximum,unsigned fields);
