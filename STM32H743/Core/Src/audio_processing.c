/*
 * audio_processing.c
 *
 *  Created on: Apr 9, 2025
 *      Author: T G Spock
 */

#include "audio_processing.h"
#include "string.h"
#include "i2s.h"

extern osThreadId_t task_audio_captHandle;
extern QueueHandle_t  queue_audio_processHandle;

// I2S DMA双缓冲区
int16_t audio_buffer_a[AUDIO_BUFFER_SIZE/2];
int16_t audio_buffer_b[AUDIO_BUFFER_SIZE/2];
volatile uint8_t current_buffer = 0; // 0=A, 1=B

void start_task_audio_capt(void *argument)
{
  // 启动DMA双缓冲模式接收
  HAL_I2S_Receive_DMA(&hi2s1, (uint16_t*)audio_buffer_a, AUDIO_BUFFER_SIZE/2);

  for(;;)
  {
    // 等待DMA传输通知
    uint32_t notification;
    if(xTaskNotifyWait(0, UINT32_MAX, &notification, portMAX_DELAY) == pdTRUE)
    {
    	audio_buffer_t audio_data;

      // 确定哪个缓冲区已满并复制数据
      if(notification == BUFFER_A_FULL)
      {
        memcpy(audio_data.samples, audio_buffer_a, sizeof(audio_buffer_a));
      }
      else
      {
        memcpy(audio_data.samples, audio_buffer_b, sizeof(audio_buffer_b));
      }

      audio_data.size = AUDIO_BUFFER_SIZE/2;
      audio_data.timestamp = HAL_GetTick();

      // 发送到处理队列
      xQueueSend(queue_audio_processHandle, &audio_data, 0);
    }
  }
}

// DMA中断回调
void HAL_I2S_RxHalfCpltCallback(I2S_HandleTypeDef *hi2s)
{
  BaseType_t xHigherPriorityTaskWoken = pdFALSE;
  xTaskNotifyFromISR(task_audio_captHandle, BUFFER_A_FULL, eSetValueWithOverwrite, &xHigherPriorityTaskWoken);
  portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void HAL_I2S_RxCpltCallback(I2S_HandleTypeDef *hi2s)
{
  BaseType_t xHigherPriorityTaskWoken = pdFALSE;
  xTaskNotifyFromISR(task_audio_captHandle, BUFFER_B_FULL, eSetValueWithOverwrite, &xHigherPriorityTaskWoken);
  portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
