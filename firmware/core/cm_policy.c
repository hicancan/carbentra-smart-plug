#include "cm_policy.h"
#include <string.h>
static bool valid_id(const char *s){
 size_t n=0;while(n<CM_ID_MAX && s[n]){unsigned char c=(unsigned char)s[n++];
 if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='-'||c=='_'))return false;}
 return n>0&&n<CM_ID_MAX;
}
static bool equal(const cm_command*a,const cm_command*b){return
 !strcmp(a->id,b->id)&&!strcmp(a->device_id,b->device_id)&&!strcmp(a->profile_id,b->profile_id)&&
 a->seq==b->seq&&a->issued_s==b->issued_s&&a->expires_s==b->expires_s&&a->action==b->action;}
cm_decision cm_evaluate(const cm_state*s,const cm_profile*p,const cm_command*c,const cm_context*x){
 cm_decision d={CM_INVALID,false,false,false};
 if(!s||!p||!x)return d;
 d.target_on=s->desired_on;
 #define REJECT(v) do{d.status=(v);return d;}while(0)
 if(x->local_trip||s->fault_latched){d.target_on=false;d.actuate=s->desired_on;d.latch_fault=true;REJECT(CM_LOCAL_TRIP);}
 if(!x->online)REJECT(CM_OFFLINE_HOLD);
 if(!c||!valid_id(c->id)||!valid_id(c->device_id)||!valid_id(c->profile_id)||!valid_id(s->device_id)||!valid_id(p->id))REJECT(CM_INVALID);
 if(!x->authenticated||!x->authorized)REJECT(CM_NO_AUTH);
 if(strcmp(c->device_id,s->device_id))REJECT(CM_WRONG_DEVICE);
 if(c->action<CM_HOLD||c->action>CM_RESTORE)REJECT(CM_INVALID);
 if(s->has_last&&!strcmp(c->id,s->last.id))REJECT(equal(c,&s->last)?CM_DUPLICATE:CM_ID_CONFLICT);
 if(!x->clock_trusted||x->wall_lower_s<=0||x->wall_upper_s<x->wall_lower_s||x->wall_upper_s-x->wall_lower_s>5)REJECT(CM_BAD_CLOCK);
 if(c->issued_s<=0||c->issued_s>x->wall_lower_s||c->expires_s<=x->wall_upper_s||c->expires_s<=c->issued_s||c->expires_s-c->issued_s>60)REJECT(CM_BAD_WINDOW);
 if(c->seq<=s->last_seq)REJECT(CM_REPLAY);
 if(!x->observation_valid||x->sampled_ms>x->mono_ms||x->mono_ms-x->sampled_ms>10000)REJECT(CM_STALE_DATA);
 if(strcmp(c->profile_id,p->id))REJECT(CM_PROFILE_MISMATCH);
 if(c->action!=CM_HOLD){
  if(!s->commissioned)REJECT(CM_NOT_COMMISSIONED);
  if(!p->approved||!strcmp(p->id,"unknown"))REJECT(CM_UNKNOWN_LOAD);
  if(p->critical)REJECT(CM_CRITICAL_LOAD);
  if(!p->allow_mains_shed)REJECT(CM_CAPABILITY_DENIED);
  bool target=c->action==CM_RESTORE;
  uint64_t dwell=s->desired_on?p->min_on_ms:p->min_off_ms;
  if(target!=s->desired_on&&(x->mono_ms<s->changed_ms||x->mono_ms-s->changed_ms<dwell))REJECT(CM_MIN_DWELL);
  d.target_on=target;d.actuate=target!=s->desired_on;
 }
 REJECT(CM_ACCEPTED);
 #undef REJECT
}
void cm_commit(cm_state*s,const cm_command*c,const cm_context*x,cm_decision d){
 if(d.latch_fault){s->fault_latched=true;s->desired_on=false;s->changed_ms=x->mono_ms;return;}
 if(d.status!=CM_ACCEPTED||!c)return;
 if(d.actuate){s->desired_on=d.target_on;s->changed_ms=x->mono_ms;}
 s->last_seq=c->seq;s->last=*c;s->has_last=true;
}
const char*cm_result_name(cm_result r){
 static const char*n[]={"ACCEPTED","DUPLICATE","LOCAL_TRIP","OFFLINE_HOLD","NO_AUTH","WRONG_DEVICE","BAD_CLOCK","BAD_WINDOW","REPLAY","ID_CONFLICT","STALE_DATA","UNKNOWN_LOAD","CRITICAL_LOAD","CAPABILITY_DENIED","PROFILE_MISMATCH","MIN_DWELL","INVALID","NOT_COMMISSIONED"};
 return (unsigned)r<sizeof(n)/sizeof(n[0])?n[r]:"INVALID";
}
