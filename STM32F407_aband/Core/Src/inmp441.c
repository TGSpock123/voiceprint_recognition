#include "inmp441.h"
#include "main.h"
#include "i2s.h"
#include "stdio.h"
#include "usart.h"

void HAL_I2S_RxCpltCallback(I2S_HandleTypeDef *hi2s)
{
	if(hi2s == &hi2s2){
		callback_cnt ++;//回调次数计数
		//将两个32整型合并为一个
		//dat32 example: 0000fffb 00004f00
		val24 = (dma[0] << 8)+(dma[1] >> 8);
		//将24位有符号整型扩展到32位
		if(val24 & 0x800000)
		{//negative
			val32 = 0xff000000 | val24;
		}else
		{
			//positive
			val32=val24;
		}
		//以采样频率的十分之一，串口发送采样值
		if(	callback_cnt % 10 == 0)
			printf("%d\r\n",val32);
	}
}

void HAL_I2S_RxHalfCpltCallback(I2S_HandleTypeDef *hi2s)
{
  // 保留
}

int fputc(int ch, FILE *f)
{
  HAL_UART_Transmit(&huart4, (uint8_t *)&ch, 1, 0xFFFF);
	return ch;
}
