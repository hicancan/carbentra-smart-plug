#include "cm_meter_decode.h"
uint16_t cm_meter_checksum(const uint16_t*r,size_t n){
 uint8_t sum=0,x=0;for(size_t i=0;i<n;i++){uint8_t hi=r[i]>>8,lo=r[i]&255;sum=(uint8_t)(sum+hi+lo);x^=hi^lo;}return (uint16_t)(((uint16_t)x<<8)|sum);
}
float cm_meter_power_factor(uint16_t r){float mag=(float)(r&0x7fff)*0.001f;return (r&0x8000)?-mag:mag;}
float cm_meter_signed_power(uint16_t r){int32_t v=(r&0x8000)?(int32_t)r-65536:(int32_t)r;return (float)v;}
uint32_t cm_crc32(const void*data,size_t n){const unsigned char*p=data;uint32_t c=0xffffffffU;for(size_t i=0;i<n;i++){c^=p[i];for(int b=0;b<8;b++)c=(c>>1)^(0xedb88320U&(0U-(c&1U)));}return ~c;}

bool cm_meter_run_state_ok(uint16_t cal,uint16_t adj,uint16_t cs1,uint16_t cs2,uint16_t e1,uint16_t e2,uint16_t status){return cal==0x8765&&adj==0x8765&&cs1==e1&&cs2==e2&&(status&0xf000)==0;}
