#include "carbentra_command_json.h"
#include "cJSON.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
static bool copy_id(cJSON*j,const char*k,char*out){
 cJSON*v=cJSON_GetObjectItemCaseSensitive(j,k);
 if(!cJSON_IsString(v)||!v->valuestring||strlen(v->valuestring)>=CARBENTRA_ID_MAX)return false;
 strcpy(out,v->valuestring);return true;
}
static bool number_s(cJSON*j,const char*k,int64_t*out){
 cJSON*v=cJSON_GetObjectItemCaseSensitive(j,k);
 if(!cJSON_IsNumber(v)||!isfinite(v->valuedouble)||v->valuedouble<1||v->valuedouble>9007199254740991.0||floor(v->valuedouble)!=v->valuedouble)return false;
 *out=(int64_t)v->valuedouble;return true;
}
bool carbentra_parse_command(const char *buf,carbentra_command*out){
 if(!buf || !out || strlen(buf)>1024 || strstr(buf,"\\u0000"))return false;
 unsigned depth=0; for(const char*z=buf;*z;z++){if(*z=='{'||*z=='[')depth++;} if(depth>16)return false;
 cJSON*j=cJSON_ParseWithLengthOpts(buf,strlen(buf)+1,NULL,true);if(!j)return false;
 bool ok=cJSON_IsObject(j);*out=(carbentra_command){0};
 ok=ok&&copy_id(j,"id",out->id)&&copy_id(j,"device_id",out->device_id)&&copy_id(j,"profile_id",out->profile_id)&&number_s(j,"issued_s",&out->issued_s)&&number_s(j,"expires_s",&out->expires_s);
 cJSON*s=cJSON_GetObjectItemCaseSensitive(j,"seq"),*a=cJSON_GetObjectItemCaseSensitive(j,"action");
 if(!cJSON_IsString(s)||!s->valuestring||!s->valuestring[0]||strlen(s->valuestring)>20)ok=false;
 else {for(const char*p=s->valuestring;*p;p++)if(*p<'0'||*p>'9')ok=false;
  char*end=NULL;errno=0;out->seq=strtoull(s->valuestring,&end,10);if(errno||!end||*end||!out->seq)ok=false;}
 if(!cJSON_IsString(a)||!a->valuestring)ok=false;
 else if(!strcmp(a->valuestring,"hold"))out->action=CARBENTRA_HOLD;
 else if(!strcmp(a->valuestring,"shed"))out->action=CARBENTRA_SHED;
 else if(!strcmp(a->valuestring,"restore"))out->action=CARBENTRA_RESTORE;
 else ok=false;
 /* Duplicate JSON keys are ambiguous and rejected. */
 for(cJSON*x=j->child;x;x=x->next)for(cJSON*y=x->next;y;y=y->next)
  if(x->string&&y->string&&!strcmp(x->string,y->string))ok=false;
 cJSON_Delete(j);return ok;
}
