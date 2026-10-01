#include "carbentra_execution.h"
#include <string.h>
void carbentra_execution_begin(carbentra_execution*x,const carbentra_command*c,bool target_on,uint64_t now){
 memset(x,0,sizeof(*x));x->command=*c;x->target_on=target_on;x->requested_ms=now;
 x->deadline_ms=now>UINT64_MAX-5000?UINT64_MAX:now+5000;x->status=CARBENTRA_EXEC_WAITING;
}
bool carbentra_execution_poll(carbentra_execution*x,uint64_t now,bool desired_on,bool fault,carbentra_feedback_status fb){
 if(!x||x->status!=CARBENTRA_EXEC_WAITING)return false;
 x->observed_ms=now;x->desired_on=desired_on;x->fault_latched=fault;x->sensing=fb;
 x->feedback_valid=fb==CARBENTRA_FB_AC_PRESENT||fb==CARBENTRA_FB_NO_AC_PULSES;
 x->output_present=fb==CARBENTRA_FB_AC_PRESENT;
 if(fault||fb==CARBENTRA_FB_PRESENT_OR_STUCK_LOW)x->status=CARBENTRA_EXEC_FAILED;
 else if(desired_on!=x->target_on)x->status=CARBENTRA_EXEC_SUPERSEDED;
 else if(now<x->requested_ms||now>=x->deadline_ms)x->status=CARBENTRA_EXEC_TIMEOUT;
 else if(now-x->requested_ms>=100&&x->feedback_valid&&x->output_present==x->target_on)x->status=CARBENTRA_EXEC_VERIFIED;
 else return false;
 x->needs_publish=true;return true;
}
const char *carbentra_execution_name(carbentra_execution_status s){
 switch(s){case CARBENTRA_EXEC_WAITING:return "REQUESTED_AWAITING_FEEDBACK";case CARBENTRA_EXEC_VERIFIED:return "OBSERVED_VERIFIED";case CARBENTRA_EXEC_FAILED:return "FAILED_FEEDBACK";case CARBENTRA_EXEC_TIMEOUT:return "TIMED_OUT";case CARBENTRA_EXEC_SUPERSEDED:return "FAILED_SUPERSEDED";default:return "INVALID";}
}
