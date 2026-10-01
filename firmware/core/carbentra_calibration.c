#include "carbentra_calibration.h"
#include "carbentra_storage_contract.h"
#include "carbentra_meter_decode.h"
#include <string.h>
#include <math.h>
bool carbentra_calibration_valid(const void *data,size_t size){
 if(!data||size!=sizeof(carbentra_calibration_record))return false;
 carbentra_calibration_record r;memcpy(&r,data,sizeof(r));
 const char board[24]=CARBENTRA_BOARD_REVISION;
 if(r.magic!=0x434d4341||r.version!=CARBENTRA_CALIBRATION_VERSION||memcmp(r.board_revision,board,sizeof(board))||!memchr(r.calibration_id,0,sizeof(r.calibration_id))||!r.calibration_id[0])return false;
 if(!isfinite(r.meter_constant_pulses_per_kwh)||r.meter_constant_pulses_per_kwh<1||r.meter_constant_pulses_per_kwh>1000000)return false;
 bool any_calibration=false,any_adjustment=false;
 for(unsigned i=0;i<11;i++)any_calibration|=r.calibration[i]!=0;
 for(unsigned i=0;i<10;i++)any_adjustment|=r.adjustment[i]!=0;
 if(!any_calibration||!any_adjustment)return false;
 return carbentra_crc32(&r,offsetof(carbentra_calibration_record,crc))==r.crc;
}
