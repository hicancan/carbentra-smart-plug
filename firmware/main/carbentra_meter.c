#include "carbentra_meter.h"
#include "carbentra_meter_decode.h"
#include "carbentra_calibration.h"
#include "carbentra_storage_contract.h"
#include <string.h>
#include <stddef.h>
#include <math.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_rom_sys.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "nvs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
static spi_device_handle_t meter;
static bool calibrated, i2c_ready;
static uint16_t expected_cs1,expected_cs2;
static float wh_per_count; static uint64_t energy_poll_ms;
static const char*TAG="carbentra_meter";
/* Factory profile, externally calibrated; never filled with made-up gains.
   CRC detects accidental damage, not malicious modification. Secure storage and
   authorized commissioning are independent release requirements. */
static esp_err_t transfer(uint8_t addr,uint16_t *v,bool read){
 uint8_t tx[3]={(uint8_t)(addr|(read?0x80:0)),(uint8_t)(*v>>8),(uint8_t)*v},rx[3]={0};
 spi_transaction_t t={.length=24,.tx_buffer=tx,.rx_buffer=rx};
 gpio_set_level(7,0);esp_err_t e=spi_device_polling_transmit(meter,&t);
 esp_rom_delay_us(5);gpio_set_level(7,1);esp_rom_delay_us(5);
 if(e==ESP_OK&&read) { *v=(uint16_t)((rx[1]<<8)|rx[2]); }
 return e;
}
static esp_err_t read_checked(uint8_t a,uint16_t*v){
 *v=0;esp_err_t e=transfer(a,v,true);if(e!=ESP_OK)return e;
 uint16_t last=0;e=transfer(0x06,&last,true);if(e!=ESP_OK||last!=*v)return ESP_ERR_INVALID_RESPONSE;
 return ESP_OK;
}
static esp_err_t write_checked(uint8_t a,uint16_t v){
 esp_err_t e=transfer(a,&v,false);if(e!=ESP_OK)return e;
 uint16_t last=0;e=transfer(0x06,&last,true);return e==ESP_OK&&last==v?ESP_OK:ESP_ERR_INVALID_RESPONSE;
}
static esp_err_t program_profile(const carbentra_calibration_record*r){
 esp_err_t e=write_checked(0x20,0x5678);if(e!=ESP_OK)return e;
 uint16_t words1[11],words2[10];memcpy(words1,r->calibration,sizeof(words1));memcpy(words2,r->adjustment,sizeof(words2));
 for(int i=0;i<11;i++)if((e=write_checked(0x21+i,words1[i]))!=ESP_OK)return e;
 uint16_t cs1=carbentra_meter_checksum(words1,11),cs2=carbentra_meter_checksum(words2,10),check;
 expected_cs1=cs1;expected_cs2=cs2;
 if((e=write_checked(0x2c,cs1))!=ESP_OK)return e;
 if((e=write_checked(0x30,0x5678))!=ESP_OK)return e;
 for(int i=0;i<10;i++)if((e=write_checked(0x31+i,words2[i]))!=ESP_OK)return e;
 if((e=write_checked(0x3b,cs2))!=ESP_OK)return e;
 if((e=write_checked(0x20,0x8765))!=ESP_OK)return e;
 if((e=write_checked(0x30,0x8765))!=ESP_OK)return e;
 if(read_checked(0x2c,&check)!=ESP_OK||check!=cs1||read_checked(0x3b,&check)!=ESP_OK||check!=cs2)return ESP_ERR_INVALID_CRC;
 if(read_checked(0x01,&check)!=ESP_OK||(check&0xf000))return ESP_ERR_INVALID_STATE;
 return ESP_OK;
}
esp_err_t carbentra_meter_start(void){
 gpio_config_t g={.pin_bit_mask=1ULL<<7,.mode=GPIO_MODE_OUTPUT};ESP_ERROR_CHECK(gpio_config(&g));gpio_set_level(7,1);
 spi_bus_config_t b={.mosi_io_num=6,.miso_io_num=5,.sclk_io_num=4,.quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=3};
 esp_err_t e=spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_DISABLED);if(e!=ESP_OK)return e;
 spi_device_interface_config_t d={.clock_speed_hz=100000,.mode=3,.spics_io_num=-1,.queue_size=1};
 if((e=spi_bus_add_device(SPI2_HOST,&d,&meter))!=ESP_OK)return e;
 i2c_config_t ic={.mode=I2C_MODE_MASTER,.sda_io_num=0,.scl_io_num=1,.sda_pullup_en=GPIO_PULLUP_DISABLE,.scl_pullup_en=GPIO_PULLUP_DISABLE,.master.clk_speed=100000};
 if(i2c_param_config(I2C_NUM_0,&ic)==ESP_OK&&i2c_driver_install(I2C_NUM_0,I2C_MODE_MASTER,0,0,0)==ESP_OK)i2c_ready=true;
 /* Reset write may invalidate immediate LastData; follow by reset-state checks. */
 uint16_t reset=0x789a;e=transfer(0,&reset,false);if(e!=ESP_OK)return e;vTaskDelay(pdMS_TO_TICKS(100));
 uint16_t a,bv;if(read_checked(0x20,&a)!=ESP_OK||read_checked(0x30,&bv)!=ESP_OK||a!=0x6886||bv!=0x6886)return ESP_ERR_INVALID_RESPONSE;
 nvs_handle_t n;e=nvs_open(CARBENTRA_NVS_FACTORY,NVS_READONLY,&n);if(e!=ESP_OK)return e;
 carbentra_calibration_record r;size_t size=sizeof(r);e=nvs_get_blob(n,"meter_cal",&r,&size);nvs_close(n);
 if(e!=ESP_OK||!carbentra_calibration_valid(&r,size)){ESP_LOGW(TAG,"No valid per-unit calibration; measurement invalid, no actuation");return ESP_ERR_INVALID_STATE;}
 e=program_profile(&r);calibrated=e==ESP_OK;
 if(calibrated){wh_per_count=100.0f/r.meter_constant_pulses_per_kwh;energy_poll_ms=esp_timer_get_time()/1000;}
 return e;
}
bool carbentra_meter_calibrated(void){return calibrated;}
esp_err_t carbentra_meter_sample(carbentra_measurement*m){
 memset(m,0,sizeof(*m));m->sampled_ms=esp_timer_get_time()/1000;m->energy_uncertain=true;
 if(i2c_ready){uint8_t reg=0,data[2];if(i2c_master_write_read_device(I2C_NUM_0,0x48,&reg,1,data,2,pdMS_TO_TICKS(30))==ESP_OK){int16_t t=(int16_t)((data[0]<<8)|data[1]);m->board_c=(t>>4)*0.0625f;m->board_temperature_valid=true;}}
 if(!calibrated)return ESP_ERR_INVALID_STATE;
 uint16_t u,i,p,q,f,pf,va,status;
 uint16_t cal,adj,cs1,cs2;
 if(read_checked(0x01,&status)!=ESP_OK||read_checked(0x20,&cal)!=ESP_OK||read_checked(0x30,&adj)!=ESP_OK||read_checked(0x2c,&cs1)!=ESP_OK||read_checked(0x3b,&cs2)!=ESP_OK||!carbentra_meter_run_state_ok(cal,adj,cs1,cs2,expected_cs1,expected_cs2,status)){calibrated=false;return ESP_ERR_INVALID_STATE;}
 m->system_status=status;
 if(read_checked(0x49,&u)!=ESP_OK||read_checked(0x48,&i)!=ESP_OK||read_checked(0x4a,&p)!=ESP_OK||read_checked(0x4b,&q)!=ESP_OK||read_checked(0x4c,&f)!=ESP_OK||read_checked(0x4d,&pf)!=ESP_OK||read_checked(0x4f,&va)!=ESP_OK)return ESP_ERR_INVALID_RESPONSE;
 if(u==0xffff||i==0xffff||f==0xffff||pf==0xffff)return ESP_ERR_INVALID_RESPONSE;
 m->volts=u*0.01f;m->amps=i*0.001f;m->watts=carbentra_meter_signed_power(p);m->vars=carbentra_meter_signed_power(q);m->hz=f*0.01f;m->pf=carbentra_meter_power_factor(pf);m->va=va;
 m->valid=isfinite(m->pf)&&fabsf(m->pf)<=1.01f;
 m->energy_interval_ms=m->sampled_ms-energy_poll_ms;m->energy_wh_per_count=wh_per_count;
 /* Both target reads are destructive: exactly one attempt, no target retry.
    An uncertain read creates a reported accounting gap, never an invented zero. */
 m->energy_forward_valid=read_checked(0x40,&m->energy_forward_counts)==ESP_OK;
 m->energy_reverse_valid=read_checked(0x41,&m->energy_reverse_counts)==ESP_OK;
 if(m->energy_interval_ms>5000){m->energy_forward_valid=false;m->energy_reverse_valid=false;}
 m->energy_uncertain=!m->energy_forward_valid||!m->energy_reverse_valid;
 energy_poll_ms=m->sampled_ms;
 return m->valid?ESP_OK:ESP_ERR_INVALID_RESPONSE;
}
