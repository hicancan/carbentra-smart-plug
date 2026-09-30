#ifndef CM_POLICY_H
#define CM_POLICY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#define CM_ID_MAX 48

typedef enum { CM_HOLD, CM_SHED, CM_RESTORE } cm_action;
typedef enum {
 CM_ACCEPTED, CM_DUPLICATE, CM_LOCAL_TRIP, CM_OFFLINE_HOLD, CM_NO_AUTH,
 CM_WRONG_DEVICE, CM_BAD_CLOCK, CM_BAD_WINDOW, CM_REPLAY, CM_ID_CONFLICT,
 CM_STALE_DATA, CM_UNKNOWN_LOAD, CM_CRITICAL_LOAD, CM_CAPABILITY_DENIED,
 CM_PROFILE_MISMATCH, CM_MIN_DWELL, CM_INVALID, CM_NOT_COMMISSIONED
} cm_result;
typedef struct {
 char id[CM_ID_MAX]; bool approved, critical, allow_mains_shed;
 uint32_t min_on_ms, min_off_ms;
} cm_profile;
typedef struct {
 char id[CM_ID_MAX], device_id[CM_ID_MAX], profile_id[CM_ID_MAX];
 uint64_t seq; int64_t issued_s, expires_s; cm_action action;
} cm_command;
typedef struct {
 bool online, authenticated, authorized, clock_trusted, observation_valid;
 bool local_trip; int64_t wall_lower_s,wall_upper_s; uint64_t mono_ms, sampled_ms;
} cm_context;
typedef struct {
 char device_id[CM_ID_MAX]; bool commissioned, desired_on, fault_latched;
 uint64_t changed_ms, last_seq; bool has_last;
 cm_command last;
} cm_state;
typedef struct { cm_result status; bool target_on, actuate, latch_fault; } cm_decision;
cm_decision cm_evaluate(const cm_state*,const cm_profile*,const cm_command*,const cm_context*);
/* Call commit only after replay journal is durable AND actuator request succeeded.
 * Actual output voltage feedback remains separate from desired_on. */
void cm_commit(cm_state*,const cm_command*,const cm_context*,cm_decision);
const char* cm_result_name(cm_result);
#endif
