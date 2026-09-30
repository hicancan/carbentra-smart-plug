#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef enum { CM_FB_UNKNOWN,CM_FB_AC_PRESENT,CM_FB_NO_AC_PULSES,CM_FB_PRESENT_OR_STUCK_LOW } cm_feedback_status;
typedef struct {
 bool initialized,level;uint64_t started_us,level_since_us,last_edge_us,last_fall_us,last_good_us,last_low_width_us;
 unsigned good_periods;
} cm_feedback_state;
void cm_feedback_init(cm_feedback_state*,uint64_t now,bool level);
void cm_feedback_edge(cm_feedback_state*,uint64_t now,bool level);
cm_feedback_status cm_feedback_classify(const cm_feedback_state*,uint64_t now);
const char*cm_feedback_name(cm_feedback_status);
