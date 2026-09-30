#include "carbentra_feedback.h"
#include <string.h>
void carbentra_feedback_init(carbentra_feedback_state*s,uint64_t now,bool level){memset(s,0,sizeof(*s));s->initialized=true;s->level=level;s->started_us=s->level_since_us=s->last_edge_us=now;}
void carbentra_feedback_edge(carbentra_feedback_state*s,uint64_t now,bool level){
 if(!s->initialized||now<s->last_edge_us){carbentra_feedback_init(s,now,level);return;}
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
carbentra_feedback_status carbentra_feedback_classify(const carbentra_feedback_state*s,uint64_t now){
 if(!s||!s->initialized||now<s->last_edge_us)return CARBENTRA_FB_UNKNOWN;
 if(!s->level&&now-s->level_since_us>=25000)return CARBENTRA_FB_PRESENT_OR_STUCK_LOW;
 if(s->good_periods>=3&&now-s->last_good_us<40000)return CARBENTRA_FB_AC_PRESENT;
 if(s->level&&now-s->last_edge_us>=40000)return CARBENTRA_FB_NO_AC_PULSES;
 return CARBENTRA_FB_UNKNOWN;
}
const char*carbentra_feedback_name(carbentra_feedback_status s){
 switch(s){case CARBENTRA_FB_AC_PRESENT:return "AC_PRESENT";case CARBENTRA_FB_NO_AC_PULSES:return "NO_AC_PULSES_DETECTED";case CARBENTRA_FB_PRESENT_OR_STUCK_LOW:return "PRESENT_OR_STUCK_LOW_FAULT";default:return "UNKNOWN";}
}
