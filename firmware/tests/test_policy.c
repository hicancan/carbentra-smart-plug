#include "carbentra_policy.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int tests;
static carbentra_state s;static carbentra_profile p;static carbentra_command c;static carbentra_context x;
static void reset(void){
 s=(carbentra_state){.device_id="CARBENTRA-TEST-001",.commissioned=true,.desired_on=true,.changed_ms=0};
 p=(carbentra_profile){.id="lamp",.approved=true,.allow_mains_shed=true,.min_on_ms=300000,.min_off_ms=300000};
 c=(carbentra_command){.id="cmd-1",.device_id="CARBENTRA-TEST-001",.profile_id="lamp",.seq=1,.issued_s=1000,.expires_s=1040,.action=CARBENTRA_SHED};
 x=(carbentra_context){.online=true,.authenticated=true,.authorized=true,.clock_trusted=true,.observation_valid=true,.wall_lower_s=1010,.wall_upper_s=1010,.mono_ms=500000,.sampled_ms=499000};
}
#define EXPECT(r) do{carbentra_decision d=carbentra_evaluate(&s,&p,&c,&x);if(d.status!=(r)){fprintf(stderr,"line %d: %s != %s\n",__LINE__,carbentra_result_name(d.status),carbentra_result_name(r));return 1;}tests++;}while(0)
int main(void){
 reset();EXPECT(CARBENTRA_ACCEPTED);
 reset();x.authenticated=false;EXPECT(CARBENTRA_NO_AUTH);
 reset();x.authorized=false;EXPECT(CARBENTRA_NO_AUTH);
 reset();strcpy(c.device_id,"elsewhere");EXPECT(CARBENTRA_WRONG_DEVICE);
 reset();c.id[0]=0;EXPECT(CARBENTRA_INVALID);
 reset();memset(c.id,'A',sizeof(c.id));EXPECT(CARBENTRA_INVALID);
 reset();strcpy(c.id,"bad/id");EXPECT(CARBENTRA_INVALID);
 reset();x.clock_trusted=false;EXPECT(CARBENTRA_BAD_CLOCK);
 reset();c.issued_s=1011;EXPECT(CARBENTRA_BAD_WINDOW);
 reset();c.expires_s=1010;EXPECT(CARBENTRA_BAD_WINDOW);
 reset();c.expires_s=1070;EXPECT(CARBENTRA_BAD_WINDOW);
 reset();c.issued_s=-1;EXPECT(CARBENTRA_BAD_WINDOW);
 reset();x.wall_upper_s=1012;c.issued_s=1011;EXPECT(CARBENTRA_BAD_WINDOW);
 reset();x.wall_upper_s=1012;c.expires_s=1012;EXPECT(CARBENTRA_BAD_WINDOW);
 reset();x.wall_upper_s=1016;EXPECT(CARBENTRA_BAD_CLOCK);
 reset();s.last_seq=1;EXPECT(CARBENTRA_REPLAY);
 reset();x.sampled_ms=500001;EXPECT(CARBENTRA_STALE_DATA);
 reset();x.sampled_ms=489999;EXPECT(CARBENTRA_STALE_DATA);
 reset();x.observation_valid=false;EXPECT(CARBENTRA_STALE_DATA);
 reset();strcpy(c.profile_id,"aircon");EXPECT(CARBENTRA_PROFILE_MISMATCH);
 reset();s.commissioned=false;EXPECT(CARBENTRA_NOT_COMMISSIONED);
 reset();p.approved=false;EXPECT(CARBENTRA_UNKNOWN_LOAD);
 reset();strcpy(p.id,"unknown");strcpy(c.profile_id,"unknown");EXPECT(CARBENTRA_UNKNOWN_LOAD);
 reset();p.critical=true;EXPECT(CARBENTRA_CRITICAL_LOAD);
 reset();p.allow_mains_shed=false;EXPECT(CARBENTRA_CAPABILITY_DENIED);
 reset();s.changed_ms=499999;EXPECT(CARBENTRA_MIN_DWELL);
 reset();s.changed_ms=600000;EXPECT(CARBENTRA_MIN_DWELL);
 reset();x.online=false;EXPECT(CARBENTRA_OFFLINE_HOLD);assert(s.desired_on);
 reset();x.local_trip=true;x.online=false;x.authenticated=false;EXPECT(CARBENTRA_LOCAL_TRIP);
 reset();s.fault_latched=true;c.action=CARBENTRA_RESTORE;EXPECT(CARBENTRA_LOCAL_TRIP);
 reset();c.action=(carbentra_action)99;EXPECT(CARBENTRA_INVALID);
 reset();carbentra_decision d=carbentra_evaluate(&s,&p,&c,&x);carbentra_commit(&s,&c,&x,d);assert(!s.desired_on);EXPECT(CARBENTRA_DUPLICATE);
 c.action=CARBENTRA_RESTORE;EXPECT(CARBENTRA_ID_CONFLICT);
 x.local_trip=true;EXPECT(CARBENTRA_LOCAL_TRIP);
 reset();c.action=CARBENTRA_HOLD;p.approved=false;s.commissioned=false;EXPECT(CARBENTRA_ACCEPTED);
 reset();s.desired_on=false;c.action=CARBENTRA_RESTORE;EXPECT(CARBENTRA_ACCEPTED);
 reset();s.desired_on=false;s.changed_ms=499000;c.action=CARBENTRA_RESTORE;EXPECT(CARBENTRA_MIN_DWELL);
 /* randomized invalid/fault property: a trip never requests on */
 for(int i=0;i<10000;i++){reset();x.local_trip=true;c.action=(carbentra_action)(i%5);x.online=i%2;d=carbentra_evaluate(&s,&p,&c,&x);assert(!d.target_on&&d.latch_fault);}
 printf("PASS %d policy cases and 10000 local-trip invariants\n",tests);return 0;
}
