#include "carbentra_policy.h"
#include <string.h>
static bool valid_id(const char *s){
 size_t n=0;while(n<CARBENTRA_ID_MAX && s[n]){unsigned char c=(unsigned char)s[n++];
 if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='-'||c=='_'))return false;}
 return n>0&&n<CARBENTRA_ID_MAX;
}
static bool equal(const carbentra_command*a,const carbentra_command*b){return
 !strcmp(a->id,b->id)&&!strcmp(a->device_id,b->device_id)&&!strcmp(a->profile_id,b->profile_id)&&
 a->seq==b->seq&&a->issued_s==b->issued_s&&a->expires_s==b->expires_s&&a->action==b->action;}
carbentra_decision carbentra_evaluate(const carbentra_state*s,const carbentra_profile*p,const carbentra_command*c,const carbentra_context*x){
 carbentra_decision d={CARBENTRA_INVALID,false,false,false};
 if(!s||!p||!x)return d;
 d.target_on=s->desired_on;
 #define REJECT(v) do{d.status=(v);return d;}while(0)
 if(x->local_trip||s->fault_latched){d.target_on=false;d.actuate=s->desired_on;d.latch_fault=true;REJECT(CARBENTRA_LOCAL_TRIP);}
 if(!x->online)REJECT(CARBENTRA_OFFLINE_HOLD);
 if(!c||!valid_id(c->id)||!valid_id(c->device_id)||!valid_id(c->profile_id)||!valid_id(s->device_id)||!valid_id(p->id))REJECT(CARBENTRA_INVALID);
 if(!x->authenticated||!x->authorized)REJECT(CARBENTRA_NO_AUTH);
 if(strcmp(c->device_id,s->device_id))REJECT(CARBENTRA_WRONG_DEVICE);
 if(c->action<CARBENTRA_HOLD||c->action>CARBENTRA_RESTORE)REJECT(CARBENTRA_INVALID);
 if(s->has_last&&!strcmp(c->id,s->last.id))REJECT(equal(c,&s->last)?CARBENTRA_DUPLICATE:CARBENTRA_ID_CONFLICT);
 if(!x->clock_trusted||x->wall_lower_s<=0||x->wall_upper_s<x->wall_lower_s||x->wall_upper_s-x->wall_lower_s>5)REJECT(CARBENTRA_BAD_CLOCK);
 if(c->issued_s<=0||c->issued_s>x->wall_lower_s||c->expires_s<=x->wall_upper_s||c->expires_s<=c->issued_s||c->expires_s-c->issued_s>60)REJECT(CARBENTRA_BAD_WINDOW);
 if(c->seq<=s->last_seq)REJECT(CARBENTRA_REPLAY);
 if(!x->observation_valid||x->sampled_ms>x->mono_ms||x->mono_ms-x->sampled_ms>10000)REJECT(CARBENTRA_STALE_DATA);
 if(strcmp(c->profile_id,p->id))REJECT(CARBENTRA_PROFILE_MISMATCH);
 if(c->action!=CARBENTRA_HOLD){
  if(!s->commissioned)REJECT(CARBENTRA_NOT_COMMISSIONED);
  if(!p->approved||!strcmp(p->id,"unknown"))REJECT(CARBENTRA_UNKNOWN_LOAD);
  if(p->critical)REJECT(CARBENTRA_CRITICAL_LOAD);
  if(!p->allow_mains_shed)REJECT(CARBENTRA_CAPABILITY_DENIED);
  bool target=c->action==CARBENTRA_RESTORE;
  uint64_t dwell=s->desired_on?p->min_on_ms:p->min_off_ms;
  if(target!=s->desired_on&&(x->mono_ms<s->changed_ms||x->mono_ms-s->changed_ms<dwell))REJECT(CARBENTRA_MIN_DWELL);
  d.target_on=target;d.actuate=target!=s->desired_on;
 }
 REJECT(CARBENTRA_ACCEPTED);
 #undef REJECT
}
void carbentra_commit(carbentra_state*s,const carbentra_command*c,const carbentra_context*x,carbentra_decision d){
 if(d.latch_fault){s->fault_latched=true;s->desired_on=false;s->changed_ms=x->mono_ms;return;}
 if(d.status!=CARBENTRA_ACCEPTED||!c)return;
 if(d.actuate){s->desired_on=d.target_on;s->changed_ms=x->mono_ms;}
 s->last_seq=c->seq;s->last=*c;s->has_last=true;
}
const char*carbentra_result_name(carbentra_result r){
 static const char*n[]={"ACCEPTED","DUPLICATE","LOCAL_TRIP","OFFLINE_HOLD","NO_AUTH","WRONG_DEVICE","BAD_CLOCK","BAD_WINDOW","REPLAY","ID_CONFLICT","STALE_DATA","UNKNOWN_LOAD","CRITICAL_LOAD","CAPABILITY_DENIED","PROFILE_MISMATCH","MIN_DWELL","INVALID","NOT_COMMISSIONED"};
 return (unsigned)r<sizeof(n)/sizeof(n[0])?n[r]:"INVALID";
}
