#include "cm_feedback.h"
#include <string.h>
void cm_feedback_init(cm_feedback_state*s,uint64_t now,bool level){memset(s,0,sizeof(*s));s->initialized=true;s->level=level;s->started_us=s->level_since_us=s->last_edge_us=now;}
void cm_feedback_edge(cm_feedback_state*s,uint64_t now,bool level){
 if(!s->initialized||now<s->last_edge_us){cm_feedback_init(s,now,level);return;}
 if(level==s->level)return;
 uint64_t width=now-s->level_since_us;
 if(width<400)s->good_periods=0;
 if(level){s->last_low_width_us=width;}
 else {
  uint64_t period=now-s->last_fall_us;
  if(s->last_fall_us&&period>=7500&&period<=11500&&width>=400&&s->last_low_width_us>=400){
   if(s->good_periods<3)s->good_periods++;
   s->last_good_us=now;
  }else s->good_periods=0;
  s->last_fall_us=now;
 }
 s->level=level;s->level_since_us=s->last_edge_us=now;
}
cm_feedback_status cm_feedback_classify(const cm_feedback_state*s,uint64_t now){
 if(!s||!s->initialized||now<s->last_edge_us)return CM_FB_UNKNOWN;
 if(!s->level&&now-s->level_since_us>=25000)return CM_FB_PRESENT_OR_STUCK_LOW;
 if(s->good_periods>=3&&now-s->last_good_us<40000)return CM_FB_AC_PRESENT;
 if(s->level&&now-s->last_edge_us>=40000)return CM_FB_NO_AC_PULSES;
 return CM_FB_UNKNOWN;
}
const char*cm_feedback_name(cm_feedback_status s){
 switch(s){case CM_FB_AC_PRESENT:return "AC_PRESENT";case CM_FB_NO_AC_PULSES:return "NO_AC_PULSES_DETECTED";case CM_FB_PRESENT_OR_STUCK_LOW:return "PRESENT_OR_STUCK_LOW_FAULT";default:return "UNKNOWN";}
}
