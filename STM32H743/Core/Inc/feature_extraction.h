/*
 * feature_extraction.h
 *
 *  Created on: Apr 9, 2025
 *      Author: T G Spock
 */

#ifndef INC_FEATURE_EXTRACTION_H_
#define INC_FEATURE_EXTRACTION_H_

#include "main.h"
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"
#include "queue.h"

// MFCC特征结构
typedef struct {
  int8_t data[39][94];
  uint32_t timestamp;
} MFCC_features_t;

#endif /* INC_FEATURE_EXTRACTION_H_ */
