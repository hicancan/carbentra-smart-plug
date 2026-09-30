#include "cm_feedback.h"
#include <assert.h>
#include <stdio.h>
static void pulse(cm_feedback_state*s,uint64_t f,uint64_t low){cm_feedback_edge(s,f,false);cm_feedback_edge(s,f+low,true);}
int main(void){cm_feedback_state s;cm_feedback_init(&s,0,true);
 assert(cm_feedback_classify(&s,1000)==CM_FB_UNKNOWN);assert(cm_feedback_classify(&s,40000)==CM_FB_NO_AC_PULSES);
 cm_feedback_init(&s,0,true);pulse(&s,1000,6000);assert(cm_feedback_classify(&s,7500)==CM_FB_UNKNOWN);
 pulse(&s,11000,6000);pulse(&s,21000,6000);pulse(&s,31000,6000);assert(cm_feedback_classify(&s,38000)==CM_FB_AC_PRESENT);
 assert(cm_feedback_classify(&s,80000)==CM_FB_NO_AC_PULSES);
 cm_feedback_init(&s,0,true);for(int i=0;i<5;i++)pulse(&s,1000+i*10000,100);assert(cm_feedback_classify(&s,42000)!=CM_FB_AC_PRESENT);
 cm_feedback_init(&s,0,true);for(int i=0;i<5;i++)pulse(&s,1000+i*8333,5500);assert(cm_feedback_classify(&s,40000)==CM_FB_AC_PRESENT);
 cm_feedback_init(&s,0,false);assert(cm_feedback_classify(&s,24999)==CM_FB_UNKNOWN);assert(cm_feedback_classify(&s,25000)==CM_FB_PRESENT_OR_STUCK_LOW);
 cm_feedback_init(&s,0,true);for(int i=0;i<6;i++)pulse(&s,1000+i*15000,5000);assert(cm_feedback_classify(&s,80000)!=CM_FB_AC_PRESENT);
 cm_feedback_init(&s,0,true);cm_feedback_edge(&s,1000,false);cm_feedback_edge(&s,900,true);assert(cm_feedback_classify(&s,950)==CM_FB_UNKNOWN);
 puts("PASS feedback qualification: 50/60Hz, startup, 3 periods, spikes, dropout, stuck LOW and time rollback");return 0;}
