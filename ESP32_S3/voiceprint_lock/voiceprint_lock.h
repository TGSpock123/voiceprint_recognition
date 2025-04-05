#pragma once
#include <stdint.h>
#include "voiceprint_model.h"
#include "voiceprint_config.h"

// 系统状态
typedef enum {
    SYSTEM_IDLE,         // 空闲状态
    SYSTEM_RECORDING,    // 录音状态
    SYSTEM_PROCESSING,   // 处理状态
    SYSTEM_UNLOCKED,     // 已解锁
    SYSTEM_ERROR        // 错误状态
} system_state_t;

// LED 闪烁模式
typedef enum {
    LED_OFF,            // 关闭
    LED_ON,             // 常亮
    LED_BLINK_SLOW,     // 慢闪
    LED_BLINK_FAST      // 快闪
} led_mode_t;

// 配置参数
#define BUTTON_PIN          4    // 按钮引脚
#define LED_PIN            5    // LED引脚
#define RELAY_PIN          6    // 继电器引脚
#define UNLOCK_TIME_MS     3000 // 开锁持续时间(ms)
#define MAX_RECORD_TIME_MS 3000 // 最大录音时间(ms)