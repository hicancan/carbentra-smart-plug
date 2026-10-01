#include "carbentra_calibration.h"
#include "carbentra_storage_contract.h"
#include "carbentra_meter_decode.h"
#include "carbentra_execution.h"
#include <string.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>
static void crc(carbentra_calibration_record*r){r->crc=carbentra_crc32(r,offsetof(carbentra_calibration_record,crc));}
int main(void){
 carbentra_calibration_record r={.magic=0x434d4341,.version=3,.board_revision=CARBENTRA_BOARD_REVISION,.calibration_id="SYNTHETIC-HOST-TEST-ONLY",.meter_constant_pulses_per_kwh=3200};
 r.calibration[0]=1;r.adjustment[0]=1;crc(&r);assert(carbentra_calibration_valid(&r,sizeof(r)));assert(!carbentra_calibration_valid(&r,102));
 r.board_revision[17]='A';crc(&r);assert(!carbentra_calibration_valid(&r,sizeof(r)));r.board_revision[17]='C';crc(&r);assert(!carbentra_calibration_valid(&r,sizeof(r)));strcpy(r.board_revision,CARBENTRA_BOARD_REVISION);
 r.calibration[0]=0;crc(&r);assert(!carbentra_calibration_valid(&r,sizeof(r)));r.calibration[0]=1;
 r.version=2;crc(&r);assert(!carbentra_calibration_valid(&r,sizeof(r)));r.version=3;
 r.meter_constant_pulses_per_kwh=NAN;crc(&r);assert(!carbentra_calibration_valid(&r,sizeof(r)));r.meter_constant_pulses_per_kwh=3200;crc(&r);r.crc^=1;assert(!carbentra_calibration_valid(&r,sizeof(r)));
 carbentra_command command={.id="cmd-one",.seq=42};carbentra_execution x;
 carbentra_execution_begin(&x,&command,true,1000);assert(x.deadline_ms==6000);assert(!carbentra_execution_poll(&x,1099,true,false,CARBENTRA_FB_AC_PRESENT));assert(carbentra_execution_poll(&x,1100,true,false,CARBENTRA_FB_AC_PRESENT));assert(x.status==CARBENTRA_EXEC_VERIFIED&&x.needs_publish&&x.command.seq==42&&!strcmp(x.command.id,"cmd-one"));assert(!carbentra_execution_poll(&x,1200,true,true,CARBENTRA_FB_UNKNOWN));
 carbentra_execution_begin(&x,&command,false,1000);assert(carbentra_execution_poll(&x,1100,false,false,CARBENTRA_FB_NO_AC_PULSES));assert(x.status==CARBENTRA_EXEC_VERIFIED&&!x.output_present);
 carbentra_execution_begin(&x,&command,true,1000);assert(!carbentra_execution_poll(&x,5999,true,false,CARBENTRA_FB_UNKNOWN));assert(carbentra_execution_poll(&x,6000,true,false,CARBENTRA_FB_AC_PRESENT));assert(x.status==CARBENTRA_EXEC_TIMEOUT);
 carbentra_execution_begin(&x,&command,true,1000);assert(carbentra_execution_poll(&x,1001,false,true,CARBENTRA_FB_UNKNOWN));assert(x.status==CARBENTRA_EXEC_FAILED);
 carbentra_execution_begin(&x,&command,true,1000);assert(carbentra_execution_poll(&x,1100,false,false,CARBENTRA_FB_NO_AC_PULSES));assert(x.status==CARBENTRA_EXEC_SUPERSEDED);
 puts("PASS calibration v3 exact board/revision/CRC and command correlated observed/failed/superseded/deadline terminal states");return 0;
}
