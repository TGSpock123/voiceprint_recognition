/*
 * audio_process.c
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

void ProcessAudio(int32_t* buffer, uint32_t size)
{
	for(uint32_t i = 0; i < size; i += 160)
	{
		// 处理音频数据
		SEGGER_RTT_printf(0, "Sample %lu: %ld\r\n", i, buffer[i]);
		HAL_Delay(10);
	}
}
