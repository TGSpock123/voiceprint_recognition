/*
 * voice_recognition.h
 *
 *  Created on: Apr 9, 2025
 *      Author: T G Spock
 */

#ifndef INC_VOICE_RECOGNITION_H_
#define INC_VOICE_RECOGNITION_H_

#include "main.h"
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"
#include "queue.h"

// 声纹数据结构
typedef struct {
  int8_t voiceprint[128]; // 模型输出的128维向量
  uint8_t isEnrolled;
  char name[20];
} voice_print_t;

#endif /* INC_VOICE_RECOGNITION_H_ */
