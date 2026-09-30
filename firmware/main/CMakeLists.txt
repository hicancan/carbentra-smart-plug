idf_component_register(SRCS "app_main.c" "cm_network.c" "cm_meter.c" "../core/cm_policy.c" "../core/cm_feedback.c" "../core/cm_command_json.c" "../core/cm_meter_decode.c"
 INCLUDE_DIRS "." "../core"
 REQUIRES esp_wifi esp_event esp_netif nvs_flash mqtt wifi_provisioning driver esp_timer esp_system json lwip)
