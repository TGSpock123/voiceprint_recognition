#ifndef INC_INMP441_H_
#define INC_INMP441_H_
#include "main.h"

uint32_t dma[4];
uint32_t val24;
int val32;
unsigned callback_cnt=0;

void HAL_I2S_RxCpltCallback(I2S_HandleTypeDef *hi2s);
void HAL_I2S_RxHalfCpltCallback(I2S_HandleTypeDef *hi2s);
void process_audio(void);



#endif /* INC_INMP441_H_ */
