#include "voiceprint_lock.h"
#include "driver/i2s.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"

static const char* TAG = "VoiceLock";
static system_state_t current_state = SYSTEM_IDLE;
static int16_t audio_buffer[AUDIO_LENGTH];
static TaskHandle_t led_task_handle = NULL;
static bool is_enrolled = false;

// LED控制任务
void led_control_task(void* pvParameters) {
    while (1) {
        switch (current_state) {
            case SYSTEM_IDLE:
                gpio_set_level(LED_PIN, 0);  // LED关闭
                vTaskDelay(pdMS_TO_TICKS(100));
                break;
            case SYSTEM_RECORDING:
                gpio_set_level(LED_PIN, 1);  // LED常亮
                vTaskDelay(pdMS_TO_TICKS(100));
                break;
            case SYSTEM_PROCESSING:
                // LED快闪
                gpio_set_level(LED_PIN, 1);
                vTaskDelay(pdMS_TO_TICKS(100));
                gpio_set_level(LED_PIN, 0);
                vTaskDelay(pdMS_TO_TICKS(100));
                break;
            case SYSTEM_UNLOCKED:
                // LED慢闪
                gpio_set_level(LED_PIN, 1);
                vTaskDelay(pdMS_TO_TICKS(500));
                gpio_set_level(LED_PIN, 0);
                vTaskDelay(pdMS_TO_TICKS(500));
                break;
            case SYSTEM_ERROR:
                // LED快速闪烁3次
                for (int i = 0; i < 3; i++) {
                    gpio_set_level(LED_PIN, 1);
                    vTaskDelay(pdMS_TO_TICKS(50));
                    gpio_set_level(LED_PIN, 0);
                    vTaskDelay(pdMS_TO_TICKS(50));
                }
                vTaskDelay(pdMS_TO_TICKS(500));
                break;
        }
    }
}

// 初始化GPIO
static void init_gpio(void) {
    // 配置按钮（输入，上拉）
    gpio_config_t btn_config = {
        .pin_bit_mask = (1ULL << BUTTON_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&btn_config);

    // 配置LED和继电器（输出）
    gpio_config_t out_config = {
        .pin_bit_mask = (1ULL << LED_PIN) | (1ULL << RELAY_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&out_config);
}

// 初始化I2S
static void init_i2s(void) {
    i2s_config_t i2s_config = {
        .mode = I2S_MODE_MASTER | I2S_MODE_RX,
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = false
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = 7,   // BCLK
        .ws_io_num = 8,    // LRCK
        .data_out_num = -1,
        .data_in_num = 9    // DATA
    };

    ESP_ERROR_CHECK(i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL));
    ESP_ERROR_CHECK(i2s_set_pin(I2S_NUM_0, &pin_config));
}

// 录音函数
static bool record_audio(void) {
    size_t bytes_read = 0;
    int64_t start_time = esp_timer_get_time();
    
    current_state = SYSTEM_RECORDING;
    
    // 等待按钮松开或达到最大录音时间
    while (gpio_get_level(BUTTON_PIN) == 0 && 
           (esp_timer_get_time() - start_time) < (MAX_RECORD_TIME_MS * 1000)) {
        
        if (i2s_read(I2S_NUM_0, audio_buffer, sizeof(audio_buffer), 
                    &bytes_read, portMAX_DELAY) != ESP_OK) {
            current_state = SYSTEM_ERROR;
            return false;
        }
    }
    
    return true;
}

// 处理声纹
static bool process_voiceprint(float* similarity) {
    current_state = SYSTEM_PROCESSING;
    
    // 预处理音频数据（添加MFCC特征提取）
    // ... 添加音频预处理代码 ...
    
    // 获取模型输入张量
    TfLiteTensor* input = interpreter->input(0);
    
    // 将预处理后的数据复制到输入张量
    // ... 数据复制代码 ...
    
    // 运行推理
    if (interpreter->Invoke() != kTfLiteOk) {
        return false;
    }
    
    // 获取输出张量
    TfLiteTensor* output = interpreter->output(0);
    
    // 计算相似度
    *similarity = calculate_similarity(output);
    
    return true;
}

// 用户注册函数
static bool enroll_user(void) {
    ESP_LOGI(TAG, "开始用户注册");
    current_state = SYSTEM_RECORDING;
    
    if (!record_audio()) {
        ESP_LOGE(TAG, "录音失败");
        return false;
    }
    
    float similarity;
    if (!process_voiceprint(&similarity)) {
        ESP_LOGE(TAG, "声纹处理失败");
        return false;
    }
    
    // 保存用户声纹特征
    // ... 保存声纹特征代码 ...
    
    is_enrolled = true;
    ESP_LOGI(TAG, "用户注册成功");
    return true;
}

// 主循环
void app_main(void) {
    // 初始化系统
    ESP_LOGI(TAG, "初始化声纹锁系统");
    init_gpio();
    init_i2s();
    
    // 创建LED控制任务
    xTaskCreate(led_control_task, "led_task", 2048, NULL, 5, &led_task_handle);
    
    // 检查是否已注册用户
    if (!is_enrolled) {
        ESP_LOGI(TAG, "未检测到用户，请按住按钮注册");
        while (!is_enrolled) {
            if (gpio_get_level(BUTTON_PIN) == 0) {
                enroll_user();
            }
            vTaskDelay(pdMS_TO_TICKS(100));
        }
    }
    
    // 主循环
    while (1) {
        if (gpio_get_level(BUTTON_PIN) == 0) {  // 按钮按下
            if (record_audio()) {
                float similarity;
                if (process_voiceprint(&similarity)) {
                    if (similarity > SIMILARITY_THRESHOLD) {
                        // 验证成功，开锁
                        current_state = SYSTEM_UNLOCKED;
                        gpio_set_level(RELAY_PIN, 1);
                        vTaskDelay(pdMS_TO_TICKS(UNLOCK_TIME_MS));
                        gpio_set_level(RELAY_PIN, 0);
                        current_state = SYSTEM_IDLE;
                    } else {
                        // 验证失败
                        current_state = SYSTEM_ERROR;
                        vTaskDelay(pdMS_TO_TICKS(1000));
                        current_state = SYSTEM_IDLE;
                    }
                }
            }
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}