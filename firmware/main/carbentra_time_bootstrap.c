#include "carbentra_time_bootstrap.h"
#include "carbentra_time_signature.h"
#include "esp_http_client.h"
#include "esp_timer.h"
#include "esp_random.h"
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <sys/time.h>
/* Untrusted HTTP transports only a public nonce and a signed time response.
 * Trust comes exclusively from an independently provisioned P-256 public key.
 * Never borrow an unverified TLS connection to bootstrap its own certificate. */
esp_err_t carbentra_time_bootstrap(const char *url,const char *public_key){
 if(!url||strncmp(url,"http://",7)||!url[7]||strchr(url,'@')||strchr(url,'?')||strchr(url,'#')||!public_key)return ESP_ERR_INVALID_ARG;
 uint32_t random[4];esp_fill_random(random,sizeof(random));char nonce[33],request[64],response[1025];
 snprintf(nonce,sizeof(nonce),"%08"PRIx32"%08"PRIx32"%08"PRIx32"%08"PRIx32,random[0],random[1],random[2],random[3]);
 int request_len=snprintf(request,sizeof(request),"{\"nonce\":\"%s\"}",nonce);
 esp_http_client_config_t config={.url=url,.timeout_ms=2000,.disable_auto_redirect=true,.method=HTTP_METHOD_POST,.buffer_size=1024};
 esp_http_client_handle_t h=esp_http_client_init(&config);if(!h)return ESP_ERR_NO_MEM;
 esp_http_client_set_header(h,"Content-Type","application/json");
 uint64_t start=esp_timer_get_time()/1000;esp_err_t result=esp_http_client_open(h,request_len);int size=0;
 if(result==ESP_OK&&esp_http_client_write(h,request,request_len)==request_len){
  int64_t declared=esp_http_client_fetch_headers(h);
  if(esp_http_client_get_status_code(h)==200&&declared>=0&&declared<=1024){
   while(size<1024){int got=esp_http_client_read(h,response+size,1024-size);if(got<0){size=-1;break;}if(!got)break;size+=got;}
   if(size>0&&size<1024&&esp_http_client_is_complete_data_received(h)&&!memchr(response,0,(size_t)size)){
    response[size]=0;uint64_t end=esp_timer_get_time()/1000;int64_t unix_s=0;
    if(end>=start&&carbentra_verify_time_response(response,nonce,public_key,end-start,&unix_s)){
     /* Add conservative transit allowance; TLS still validates CA/hostname/date. */
     struct timeval tv={.tv_sec=unix_s+(int64_t)((end-start+999)/1000),.tv_usec=0};
     result=settimeofday(&tv,NULL)==0?ESP_OK:ESP_FAIL;
    }else result=ESP_ERR_INVALID_RESPONSE;
   }else result=ESP_ERR_INVALID_SIZE;
  }else result=ESP_ERR_INVALID_RESPONSE;
 }else if(result==ESP_OK)result=ESP_FAIL;
 esp_http_client_close(h);esp_http_client_cleanup(h);return result;
}
