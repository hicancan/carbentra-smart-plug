#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef enum { CARBENTRA_FB_UNKNOWN,CARBENTRA_FB_AC_PRESENT,CARBENTRA_FB_NO_AC_PULSES,CARBENTRA_FB_PRESENT_OR_STUCK_LOW } carbentra_feedback_status;
typedef struct {
 bool initialized,level;uint64_t started_us,level_since_us,last_edge_us,last_fall_us,last_good_us,last_low_width_us;
 unsigned good_periods;
} carbentra_feedback_state;
void carbentra_feedback_init(carbentra_feedback_state*,uint64_t now,bool level);
void carbentra_feedback_edge(carbentra_feedback_state*,uint64_t now,bool level);
carbentra_feedback_status carbentra_feedback_classify(const carbentra_feedback_state*,uint64_t now);
const char*carbentra_feedback_name(carbentra_feedback_status);
