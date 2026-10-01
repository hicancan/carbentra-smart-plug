#pragma once
#include "carbentra_policy.h"
#include "carbentra_feedback.h"
typedef enum {CARBENTRA_EXEC_IDLE,CARBENTRA_EXEC_WAITING,CARBENTRA_EXEC_VERIFIED,CARBENTRA_EXEC_FAILED,CARBENTRA_EXEC_TIMEOUT,CARBENTRA_EXEC_SUPERSEDED} carbentra_execution_status;
typedef struct {
 carbentra_command command;carbentra_execution_status status;
 bool target_on,desired_on,needs_publish,feedback_valid,output_present,fault_latched;
 carbentra_feedback_status sensing;
 uint64_t requested_ms,deadline_ms,observed_ms;
} carbentra_execution;
void carbentra_execution_begin(carbentra_execution*,const carbentra_command*,bool target_on,uint64_t now);
bool carbentra_execution_poll(carbentra_execution*,uint64_t now,bool desired_on,bool fault,carbentra_feedback_status);
const char *carbentra_execution_name(carbentra_execution_status);
