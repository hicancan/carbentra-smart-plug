#include "carbentra_time_signature.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static int read_file(const char*path,char *out,size_t capacity){FILE*f=fopen(path,"rb");if(!f)return 0;size_t n=fread(out,1,capacity-1,f);int extra=fgetc(f);fclose(f);out[n]=0;return extra==EOF;}
int main(int argc,char**argv){if(argc!=5)return 2;char pem[2048],json[4096];if(!read_file(argv[1],pem,sizeof(pem))||!read_file(argv[2],json,sizeof(json)))return 2;int64_t unix_s=0;bool ok=carbentra_verify_time_response(json,argv[3],pem,strtoull(argv[4],NULL,10),&unix_s);if(ok)printf("%"PRId64"\n",unix_s);return ok?0:1;}
