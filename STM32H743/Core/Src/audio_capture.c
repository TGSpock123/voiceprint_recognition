/*
 * audio_capture.c
 *
 *  Created on: Apr 11, 2025
 *      Author: T G Spock
 */

#include "main.h"
#include <stdio.h>
#include <string.h>
#include "audio_capture.h"
#include "SEGGER_RTT.h"
#include "SEGGER_RTT_Conf.h"

/* 外部变量引用 */
extern I2S_HandleTypeDef hi2s1;

/* DMA缓冲区 */
uint32_t dma[DMA_BUFFER_SIZE];

/* 主音频缓冲区（3秒数据） */
int32_t audioBuffer[AUDIO_BUFFER_SAMPLES];

/* 控制变量 */
volatile AudioState_t audioState = AUDIO_STATE_IDLE;
volatile uint32_t currentSampleIndex = 0;
volatile uint8_t captureDoneFlag = 0;

/**
  * @brief  初始化音频采集
  * @retval None
  */
void AudioCapture_Init(void)
{
    /* 清空缓冲区 */
    memset(dma, 0, DMA_BUFFER_SIZE * sizeof(uint32_t));
    memset(audioBuffer, 0, AUDIO_BUFFER_SAMPLES * sizeof(uint32_t));
    currentSampleIndex = 0;

    /* 设置初始状态 */
    audioState = AUDIO_STATE_IDLE;
    captureDoneFlag = 0;

    SEGGER_RTT_printf(0, "Audio capture system initialized. Press button to start 3-second capture.\r\n");
}

/**
  * @brief  启动音频采集
  * @retval None
  */
void AudioCapture_Start(void)
{
    /* 只有在空闲状态才启动采集 */
    if(audioState == AUDIO_STATE_IDLE)
    {
        SEGGER_RTT_printf(0, "Starting audio capture...\r\n");

        /* 重置状态 */
        captureDoneFlag = 0;
        audioState = AUDIO_STATE_CAPTURING;
        currentSampleIndex = 0;

        /* 清空缓冲区 */
        memset(dma, 0, DMA_BUFFER_SIZE * sizeof(uint32_t));

        /* 启动I2S DMA接收 */
        HAL_I2S_Receive_DMA(&hi2s1, (uint16_t*)dma, DMA_BUFFER_SIZE);
    }
}

/**
  * @brief  停止音频采集
  * @retval None
  */
void AudioCapture_Stop(void)
{
    /* 停止DMA传输 */
    HAL_I2S_DMAStop(&hi2s1);

    SEGGER_RTT_printf(0, "Audio capture completed. Collected %d samples.\r\n", AUDIO_BUFFER_SAMPLES);

    /* 更新状态 */
    audioState = AUDIO_STATE_PROCESSING;
    captureDoneFlag = 1;
}

/**
 * @brief DMA全传输完成回调
 */
void HAL_I2S_RxCpltCallback(I2S_HandleTypeDef *hi2s)
{
    if(hi2s != &hi2s1 || audioState != AUDIO_STATE_CAPTURING)
        return;

    // 合并两个32位值获取一个24位样本
    uint32_t val24 = (dma[0]<<8)+(dma[1]>>8);
    int32_t val32;

    // 将24位有符号整型扩展到32位
    if(val24 & 0x800000) { // 负数
        val32 = 0xff000000 | val24;
    } else { // 正数
        val32 = val24;
    }

    // 保存样本，并检查是否达到上限
    if(currentSampleIndex < AUDIO_BUFFER_SAMPLES) {
        audioBuffer[currentSampleIndex++] = val32;
    } else {
        // 已采集足够样本，停止DMA
        AudioCapture_Stop();
        return;
    }

    // 重启DMA以继续采集
    if(currentSampleIndex < AUDIO_BUFFER_SAMPLES && audioState == AUDIO_STATE_CAPTURING) {
        HAL_I2S_Receive_DMA(&hi2s1, (uint16_t*)dma, DMA_BUFFER_SIZE);
    }
}
/**
  * @brief  按键中断处理函数
  * @retval None
  */
void EXTI13_IRQHandler(void)
{
    /* 清除中断标志 */
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_13);
}

/**
  * @brief  按键外部中断回调
  * @param  GPIO_Pin: 触发中断的GPIO引脚
  * @retval None
  */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if(GPIO_Pin == GPIO_PIN_13)
    {
        /* 防抖 - 可根据需要调整 */
        static uint32_t lastTick = 0;
        uint32_t currentTick = HAL_GetTick();

        if(currentTick - lastTick > 300)  // 300ms防抖
        {
            /* 只有在空闲状态才处理按键 */
            if(audioState == AUDIO_STATE_IDLE)
            {
                /* 直接启动采集 */
                AudioCapture_Start();
            }

            lastTick = currentTick;
        }
    }
}
