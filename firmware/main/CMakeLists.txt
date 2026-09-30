idf_component_register(SRCS "app_main.c" "carbentra_network.c" "carbentra_meter.c" "../core/carbentra_policy.c" "../core/carbentra_feedback.c" "../core/carbentra_command_json.c" "../core/carbentra_meter_decode.c"
 INCLUDE_DIRS "." "../core"
 REQUIRES esp_wifi esp_event esp_netif nvs_flash mqtt wifi_provisioning driver esp_timer esp_system json lwip)
