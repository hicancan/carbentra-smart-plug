#include "cm_policy.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int tests;
static cm_state s;static cm_profile p;static cm_command c;static cm_context x;
static void reset(void){
 s=(cm_state){.device_id="CM-TEST-001",.commissioned=true,.desired_on=true,.changed_ms=0};
 p=(cm_profile){.id="lamp",.approved=true,.allow_mains_shed=true,.min_on_ms=300000,.min_off_ms=300000};
 c=(cm_command){.id="cmd-1",.device_id="CM-TEST-001",.profile_id="lamp",.seq=1,.issued_s=1000,.expires_s=1040,.action=CM_SHED};
 x=(cm_context){.online=true,.authenticated=true,.authorized=true,.clock_trusted=true,.observation_valid=true,.wall_lower_s=1010,.wall_upper_s=1010,.mono_ms=500000,.sampled_ms=499000};
}
#define EXPECT(r) do{cm_decision d=cm_evaluate(&s,&p,&c,&x);if(d.status!=(r)){fprintf(stderr,"line %d: %s != %s\n",__LINE__,cm_result_name(d.status),cm_result_name(r));return 1;}tests++;}while(0)
int main(void){
 reset();EXPECT(CM_ACCEPTED);
 reset();x.authenticated=false;EXPECT(CM_NO_AUTH);
 reset();x.authorized=false;EXPECT(CM_NO_AUTH);
 reset();strcpy(c.device_id,"elsewhere");EXPECT(CM_WRONG_DEVICE);
 reset();c.id[0]=0;EXPECT(CM_INVALID);
 reset();memset(c.id,'A',sizeof(c.id));EXPECT(CM_INVALID);
 reset();strcpy(c.id,"bad/id");EXPECT(CM_INVALID);
 reset();x.clock_trusted=false;EXPECT(CM_BAD_CLOCK);
 reset();c.issued_s=1011;EXPECT(CM_BAD_WINDOW);
 reset();c.expires_s=1010;EXPECT(CM_BAD_WINDOW);
 reset();c.expires_s=1070;EXPECT(CM_BAD_WINDOW);
 reset();c.issued_s=-1;EXPECT(CM_BAD_WINDOW);
 reset();x.wall_upper_s=1012;c.issued_s=1011;EXPECT(CM_BAD_WINDOW);
 reset();x.wall_upper_s=1012;c.expires_s=1012;EXPECT(CM_BAD_WINDOW);
 reset();x.wall_upper_s=1016;EXPECT(CM_BAD_CLOCK);
 reset();s.last_seq=1;EXPECT(CM_REPLAY);
 reset();x.sampled_ms=500001;EXPECT(CM_STALE_DATA);
 reset();x.sampled_ms=489999;EXPECT(CM_STALE_DATA);
 reset();x.observation_valid=false;EXPECT(CM_STALE_DATA);
 reset();strcpy(c.profile_id,"aircon");EXPECT(CM_PROFILE_MISMATCH);
 reset();s.commissioned=false;EXPECT(CM_NOT_COMMISSIONED);
 reset();p.approved=false;EXPECT(CM_UNKNOWN_LOAD);
 reset();strcpy(p.id,"unknown");strcpy(c.profile_id,"unknown");EXPECT(CM_UNKNOWN_LOAD);
 reset();p.critical=true;EXPECT(CM_CRITICAL_LOAD);
 reset();p.allow_mains_shed=false;EXPECT(CM_CAPABILITY_DENIED);
 reset();s.changed_ms=499999;EXPECT(CM_MIN_DWELL);
 reset();s.changed_ms=600000;EXPECT(CM_MIN_DWELL);
 reset();x.online=false;EXPECT(CM_OFFLINE_HOLD);assert(s.desired_on);
 reset();x.local_trip=true;x.online=false;x.authenticated=false;EXPECT(CM_LOCAL_TRIP);
 reset();s.fault_latched=true;c.action=CM_RESTORE;EXPECT(CM_LOCAL_TRIP);
 reset();c.action=(cm_action)99;EXPECT(CM_INVALID);
 reset();cm_decision d=cm_evaluate(&s,&p,&c,&x);cm_commit(&s,&c,&x,d);assert(!s.desired_on);EXPECT(CM_DUPLICATE);
 c.action=CM_RESTORE;EXPECT(CM_ID_CONFLICT);
 x.local_trip=true;EXPECT(CM_LOCAL_TRIP);
 reset();c.action=CM_HOLD;p.approved=false;s.commissioned=false;EXPECT(CM_ACCEPTED);
 reset();s.desired_on=false;c.action=CM_RESTORE;EXPECT(CM_ACCEPTED);
 reset();s.desired_on=false;s.changed_ms=499000;c.action=CM_RESTORE;EXPECT(CM_MIN_DWELL);
 /* randomized invalid/fault property: a trip never requests on */
 for(int i=0;i<10000;i++){reset();x.local_trip=true;c.action=(cm_action)(i%5);x.online=i%2;d=cm_evaluate(&s,&p,&c,&x);assert(!d.target_on&&d.latch_fault);}
 printf("PASS %d policy cases and 10000 local-trip invariants\n",tests);return 0;
}
