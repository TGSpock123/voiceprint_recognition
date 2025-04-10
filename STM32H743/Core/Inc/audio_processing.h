/*
 * audio_processing.h
 *
 *  Created on: Apr 9, 2025
 *      Author: T G Spock
 */

#ifndef INC_AUDIO_PROCESSING_H_
#define INC_AUDIO_PROCESSING_H_

#include "main.h"
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"
#include "queue.h"

#define AUDIO_SAMPLE_RATE   			16000
#define AUDIO_BUFFER_SIZE   				48000   	// 3秒音频
#define AUDIO_FRAME_SIZE                (AUDIO_BUFFER_SIZE / 2)
#define NUM_USERS           					3    		 	// 支持的用户数量
#define RECOGNITION_THRESHOLD 	0.75  		// 识别阈值
#define BUFFER_A_FULL 0
#define BUFFER_B_FULL 1

// 音频数据缓冲区结构
typedef struct {
  int16_t samples[AUDIO_FRAME_SIZE];
  uint32_t size;
  uint32_t timestamp;
} audio_buffer_t;

#endif /* INC_AUDIO_PROCESSING_H_ */
