#include "mbedtls/x509_crt.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static int load(const char*path,mbedtls_x509_crt*cert){FILE*f=fopen(path,"rb");if(!f)return -1;unsigned char data[8192];size_t n=fread(data,1,sizeof(data)-1,f);fclose(f);data[n]=0;return mbedtls_x509_crt_parse(cert,data,n+1);}
int main(int argc,char**argv){if(argc!=4)return 2;mbedtls_x509_crt root,leaf;mbedtls_x509_crt_init(&root);mbedtls_x509_crt_init(&leaf);uint32_t flags=0;int result=load(argv[1],&root)||load(argv[2],&leaf);if(!result)result=mbedtls_x509_crt_verify(&leaf,&root,NULL,argv[3],&flags,NULL,NULL);printf("flags=%u\n",flags);mbedtls_x509_crt_free(&root);mbedtls_x509_crt_free(&leaf);return result?1:0;}
