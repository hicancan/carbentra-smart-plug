#include "cm_command_json.h"
#include "cm_meter_decode.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
int main(void){cm_command c;
 const char *good="{\"id\":\"a\",\"device_id\":\"CM-1\",\"profile_id\":\"lamp\",\"seq\":\"18446744073709551615\",\"issued_s\":1000,\"expires_s\":1040,\"action\":\"hold\"}";
 assert(cm_parse_command(good,&c));assert(c.seq==UINT64_MAX);
 const char *bad[]={"{}","[]","null","", "{\"id\":\"a\",\"id\":\"b\"}","{\"id\":", "{\"seq\":1}","{\"seq\":\"18446744073709551616\"}"};
 for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);i++)assert(!cm_parse_command(bad[i],&c));
 char copy[1025];strcpy(copy,good);char*q=strstr(copy,"1000");memcpy(q,"1e99",4);assert(!cm_parse_command(copy,&c));
 strcpy(copy,good);q=strstr(copy,"18446744073709551615");memcpy(q,"18446744073709551616",20);assert(!cm_parse_command(copy,&c));
 strcpy(copy,good);q=strstr(copy,"\"a\"");q[0]='\n';assert(!cm_parse_command(copy,&c));
 assert(cm_meter_signed_power(0xffff)==-1);assert(cm_meter_signed_power(0x8000)==-32768);assert(cm_meter_signed_power(0x7fff)==32767);
 assert(fabsf(cm_meter_power_factor(0x03e8)-1)<1e-5);assert(fabsf(cm_meter_power_factor(0x83e8)+1)<1e-5);assert(cm_meter_power_factor(0x8000)==0);
 uint16_t r[]={0x1234,0xabcd};assert(cm_meter_checksum(r,2)==0x40be);assert(cm_crc32("123456789",9)==0xcbf43926);
 assert(cm_meter_run_state_ok(0x8765,0x8765,0x1234,0x5678,0x1234,0x5678,0));
 assert(!cm_meter_run_state_ok(0x6886,0x6886,0,0,0,0,0));
 assert(!cm_meter_run_state_ok(0,0,0,0,0,0,0));
 assert(!cm_meter_run_state_ok(0xffff,0xffff,0xffff,0xffff,0xffff,0xffff,0xffff));
 assert(!cm_meter_run_state_ok(0x8765,0x8765,0x1234,0x5679,0x1234,0x5678,0));
 assert(!cm_meter_run_state_ok(0x8765,0x8765,0x1234,0x5678,0x1234,0x5678,0xf000));
 puts("PASS JSON boundaries, meter encodings/checksum/CRC, runtime reset and stuck-link regression");return 0;}
