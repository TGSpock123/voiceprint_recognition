/*
 * feature_extraction.c
 *
 *  Created on: Apr 9, 2025
 *      Author: T G Spock
 */

#include "feature_extraction.h"
#include "arm_math.h"
#include "audio_processing.h"
#include "SEGGER_RTT.h"
#include "SEGGER_RTT_Conf.h"

extern osThreadId_t task_feature_exHandle;
extern QueueHandle_t  queue_audio_processHandle;
extern QueueHandle_t  queue_feature_inferenceHandle;

void start_task_feature_extr(void *argument)
{
	audio_buffer_t audio_data;

	for(;;)
	{
		if(pdTRUE == xQueueReceive(queue_audio_processHandle, &audio_data, portMAX_DELAY))
		{
			SEGGER_RTT_printf(0, "buffer receive:");
		}
	}
}
