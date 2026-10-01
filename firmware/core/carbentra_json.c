#include "carbentra_json.h"
#include <stdbool.h>
#include <string.h>
cJSON *carbentra_json_object(const char*text,size_t maximum,unsigned fields){
 if(!text||strlen(text)>maximum||strstr(text,"\\u0000"))return NULL;
 unsigned depth=0;bool quoted=false,escaped=false;
 for(const char*p=text;*p;p++){
  if(quoted){if(escaped)escaped=false;else if(*p=='\\')escaped=true;else if(*p=='\"')quoted=false;}
  else if(*p=='\"')quoted=true;
  else if(*p=='{'||*p=='['){if(++depth>8)return NULL;}
  else if(*p=='}'||*p==']'){if(!depth)return NULL;--depth;}
 }
 if(quoted||depth)return NULL;
 cJSON*j=cJSON_ParseWithLengthOpts(text,strlen(text)+1,NULL,true);if(!j)return NULL;
 bool ok=cJSON_IsObject(j)&&(!fields||cJSON_GetArraySize(j)==(int)fields);
 for(cJSON*x=j->child;x;x=x->next)for(cJSON*y=x->next;y;y=y->next)if(x->string&&y->string&&!strcmp(x->string,y->string))ok=false;
 if(!ok){cJSON_Delete(j);return NULL;}return j;
}
