#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_driver_gpio.h"
//#include "voiceprint_recognition.cpp"

#define TAG "MAIN"
#define LOCK_GPIO 33  // 根据实际连接调整

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "声纹锁系统启动");
    
    // 初始化锁控制GPIO
    gpio_config_t io_conf = {};
    io_conf.pin_bit_mask = (1ULL << LOCK_GPIO);
    io_conf.mode = GPIO_MODE_OUTPUT;
    gpio_config(&io_conf);
    gpio_set_level(LOCK_GPIO, 0); // 默认锁定
    
    // 初始化音频
    initializeAudio();
    
    // 初始化声纹识别
    VoiceprintRecognition recognizer;
    if (!recognizer.Initialize()) {
        ESP_LOGE(TAG, "声纹识别初始化失败");
        return;
    }
    
    // 注册示例用户
    ESP_LOGI(TAG, "系统将注册一个示例用户");
    ESP_LOGI(TAG, "准备录音，3秒后开始...");
    vTaskDelay(pdMS_TO_TICKS(3000));
    
    if (!recognizer.RegisterUser(0)) {
        ESP_LOGE(TAG, "用户注册失败");
        return;
    }
    
    // 主循环
    while (1) {
        ESP_LOGI(TAG, "按下按钮开始识别...");
        
        // 实际项目中，这里应添加按钮触发代码
        vTaskDelay(pdMS_TO_TICKS(5000));
        
        int user_id = recognizer.RecognizeUser();
        if (user_id >= 0) {
            ESP_LOGI(TAG, "验证通过，开锁");
            gpio_set_level(LOCK_GPIO, 1); // 开锁
            vTaskDelay(pdMS_TO_TICKS(3000));
            gpio_set_level(LOCK_GPIO, 0); // 锁定
        } else {
            ESP_LOGI(TAG, "验证失败");
        }
    }
}