#ifndef CARBENTRA_POLICY_H
#define CARBENTRA_POLICY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#define CARBENTRA_ID_MAX 48

typedef enum { CARBENTRA_HOLD, CARBENTRA_SHED, CARBENTRA_RESTORE } carbentra_action;
typedef enum {
 CARBENTRA_ACCEPTED, CARBENTRA_DUPLICATE, CARBENTRA_LOCAL_TRIP, CARBENTRA_OFFLINE_HOLD, CARBENTRA_NO_AUTH,
 CARBENTRA_WRONG_DEVICE, CARBENTRA_BAD_CLOCK, CARBENTRA_BAD_WINDOW, CARBENTRA_REPLAY, CARBENTRA_ID_CONFLICT,
 CARBENTRA_STALE_DATA, CARBENTRA_UNKNOWN_LOAD, CARBENTRA_CRITICAL_LOAD, CARBENTRA_CAPABILITY_DENIED,
 CARBENTRA_PROFILE_MISMATCH, CARBENTRA_MIN_DWELL, CARBENTRA_INVALID, CARBENTRA_NOT_COMMISSIONED
} carbentra_result;
typedef struct {
 char id[CARBENTRA_ID_MAX]; bool approved, critical, allow_mains_shed;
 uint32_t min_on_ms, min_off_ms;
} carbentra_profile;
typedef struct {
 char id[CARBENTRA_ID_MAX], device_id[CARBENTRA_ID_MAX], profile_id[CARBENTRA_ID_MAX];
 uint64_t seq; int64_t issued_s, expires_s; carbentra_action action;
} carbentra_command;
typedef struct {
 bool online, authenticated, authorized, clock_trusted, observation_valid;
 bool local_trip; int64_t wall_lower_s,wall_upper_s; uint64_t mono_ms, sampled_ms;
} carbentra_context;
typedef struct {
 char device_id[CARBENTRA_ID_MAX]; bool commissioned, desired_on, fault_latched;
 uint64_t changed_ms, last_seq; bool has_last;
 carbentra_command last;
} carbentra_state;
typedef struct { carbentra_result status; bool target_on, actuate, latch_fault; } carbentra_decision;
carbentra_decision carbentra_evaluate(const carbentra_state*,const carbentra_profile*,const carbentra_command*,const carbentra_context*);
/* Call commit only after replay journal is durable AND actuator request succeeded.
 * Actual output voltage feedback remains separate from desired_on. */
void carbentra_commit(carbentra_state*,const carbentra_command*,const carbentra_context*,carbentra_decision);
const char* carbentra_result_name(carbentra_result);
#endif
