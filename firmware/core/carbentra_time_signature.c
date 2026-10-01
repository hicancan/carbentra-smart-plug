#include "carbentra_time_signature.h"
#include "cJSON.h"
#include "carbentra_json.h"
#include "mbedtls/pk.h"
#include "mbedtls/md.h"
#include "mbedtls/base64.h"
#include <string.h>
#include <stdio.h>
#include <inttypes.h>
#include <math.h>
#ifndef MBEDTLS_PRIVATE
#define MBEDTLS_PRIVATE(member) member
#endif
bool carbentra_verify_time_response(const char *json,const char *nonce,const char *public_pem,uint64_t elapsed_ms,int64_t *unix_s){
 if(!json||!nonce||!public_pem||!unix_s||strlen(json)>1024||strlen(nonce)!=32||elapsed_ms>2000||strstr(json,"\\u0000"))return false;
 for(const char*p=nonce;*p;p++)if(!((*p>='0'&&*p<='9')||(*p>='a'&&*p<='f')))return false;
 cJSON*j=carbentra_json_object(json,1024,3);if(!j)return false;
 cJSON*n=cJSON_GetObjectItemCaseSensitive(j,"nonce"),*t=cJSON_GetObjectItemCaseSensitive(j,"unix_s"),*s=cJSON_GetObjectItemCaseSensitive(j,"signature");
 bool ok=cJSON_IsObject(j)&&cJSON_GetArraySize(j)==3&&cJSON_IsString(n)&&!strcmp(n->valuestring,nonce)&&cJSON_IsNumber(t)&&isfinite(t->valuedouble)&&floor(t->valuedouble)==t->valuedouble&&t->valuedouble>=1700000000&&t->valuedouble<4102444800.0&&cJSON_IsString(s)&&strlen(s->valuestring)<=128;
 for(cJSON*x=j->child;x;x=x->next)for(cJSON*y=x->next;y;y=y->next)if(x->string&&y->string&&!strcmp(x->string,y->string))ok=false;
 unsigned char signature[96],hash[32];size_t siglen=0;char message[96];
 mbedtls_pk_context key;mbedtls_pk_init(&key);
 if(ok){
  int written=snprintf(message,sizeof(message),"CARBENTRA_TIME_V1\n%s\n%"PRId64"\n",nonce,(int64_t)t->valuedouble);
  ok=written>0&&(size_t)written<sizeof(message)&&mbedtls_base64_decode(signature,sizeof(signature),&siglen,(unsigned char*)s->valuestring,strlen(s->valuestring))==0&&siglen>0;
  if(ok)ok=mbedtls_pk_parse_public_key(&key,(const unsigned char*)public_pem,strlen(public_pem)+1)==0;
  if(ok)ok=mbedtls_pk_can_do(&key,MBEDTLS_PK_ECDSA)&&mbedtls_pk_get_bitlen(&key)==256&&mbedtls_pk_ec(key)->MBEDTLS_PRIVATE(grp).id==MBEDTLS_ECP_DP_SECP256R1;
  if(ok)ok=mbedtls_md(mbedtls_md_info_from_type(MBEDTLS_MD_SHA256),(const unsigned char*)message,(size_t)written,hash)==0&&mbedtls_pk_verify(&key,MBEDTLS_MD_SHA256,hash,sizeof(hash),signature,siglen)==0;
 }
 if(ok)*unix_s=(int64_t)t->valuedouble;
 mbedtls_pk_free(&key);cJSON_Delete(j);return ok;
}
