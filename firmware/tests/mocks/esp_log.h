#pragma once
static inline void mock_log(const char*tag,const char*format,...){(void)tag;(void)format;}
#define ESP_LOGE(...) mock_log(__VA_ARGS__)
#define ESP_LOGW(...) mock_log(__VA_ARGS__)
#define ESP_LOGI(...) mock_log(__VA_ARGS__)
