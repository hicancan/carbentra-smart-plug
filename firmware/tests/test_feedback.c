#include "carbentra_feedback.h"
#include <assert.h>
#include <stdio.h>
static void pulse(carbentra_feedback_state*s,uint64_t f,uint64_t low){carbentra_feedback_edge(s,f,false);carbentra_feedback_edge(s,f+low,true);}
int main(void){carbentra_feedback_state s;carbentra_feedback_init(&s,0,true);
 assert(carbentra_feedback_classify(&s,1000)==CARBENTRA_FB_UNKNOWN);assert(carbentra_feedback_classify(&s,40000)==CARBENTRA_FB_NO_AC_PULSES);
 carbentra_feedback_init(&s,0,true);pulse(&s,1000,6000);assert(carbentra_feedback_classify(&s,7500)==CARBENTRA_FB_UNKNOWN);
 pulse(&s,11000,6000);pulse(&s,21000,6000);pulse(&s,31000,6000);assert(carbentra_feedback_classify(&s,38000)==CARBENTRA_FB_AC_PRESENT);
 assert(carbentra_feedback_classify(&s,80000)==CARBENTRA_FB_NO_AC_PULSES);
 carbentra_feedback_init(&s,0,true);for(int i=0;i<5;i++)pulse(&s,1000+i*10000,100);assert(carbentra_feedback_classify(&s,42000)!=CARBENTRA_FB_AC_PRESENT);
 carbentra_feedback_init(&s,0,true);for(int i=0;i<5;i++)pulse(&s,1000+i*8333,5500);assert(carbentra_feedback_classify(&s,40000)==CARBENTRA_FB_AC_PRESENT);
 carbentra_feedback_init(&s,0,false);assert(carbentra_feedback_classify(&s,24999)==CARBENTRA_FB_UNKNOWN);assert(carbentra_feedback_classify(&s,25000)==CARBENTRA_FB_PRESENT_OR_STUCK_LOW);
 carbentra_feedback_init(&s,0,true);for(int i=0;i<6;i++)pulse(&s,1000+i*15000,5000);assert(carbentra_feedback_classify(&s,80000)!=CARBENTRA_FB_AC_PRESENT);
 carbentra_feedback_init(&s,0,true);carbentra_feedback_edge(&s,1000,false);carbentra_feedback_edge(&s,900,true);assert(carbentra_feedback_classify(&s,950)==CARBENTRA_FB_UNKNOWN);
 puts("PASS feedback qualification: 50/60Hz, startup, 3 periods, spikes, dropout, stuck LOW and time rollback");return 0;}
