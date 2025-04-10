/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "queue.h"
#include "audio_processing.h"
#include "feature_extraction.h"
#include "voice_recognition.h"
#include "user_interface.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */

/* USER CODE END Variables */
/* Definitions for task_audio_capt */
osThreadId_t task_audio_captHandle;
const osThreadAttr_t task_audio_capt_attributes = {
  .name = "task_audio_capt",
  .stack_size = 256 * 4,
  .priority = (osPriority_t) osPriorityHigh,
};
/* Definitions for task_feature_ex */
osThreadId_t task_feature_exHandle;
const osThreadAttr_t task_feature_ex_attributes = {
  .name = "task_feature_ex",
  .stack_size = 2048 * 4,
  .priority = (osPriority_t) osPriorityAboveNormal,
};
/* Definitions for task_ai_inter */
osThreadId_t task_ai_interHandle;
const osThreadAttr_t task_ai_inter_attributes = {
  .name = "task_ai_inter",
  .stack_size = 8192 * 4,
  .priority = (osPriority_t) osPriorityBelowNormal,
};
/* Definitions for task_result */
osThreadId_t task_resultHandle;
const osThreadAttr_t task_result_attributes = {
  .name = "task_result",
  .stack_size = 1024 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for task_user_inter */
osThreadId_t task_user_interHandle;
const osThreadAttr_t task_user_inter_attributes = {
  .name = "task_user_inter",
  .stack_size = 256 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for queue_audio_process */
osMessageQueueId_t queue_audio_processHandle;
const osMessageQueueAttr_t queue_audio_process_attributes = {
  .name = "queue_audio_process"
};
/* Definitions for queue_feature_inference */
osMessageQueueId_t queue_feature_inferenceHandle;
const osMessageQueueAttr_t queue_feature_inference_attributes = {
  .name = "queue_feature_inference"
};
/* Definitions for queue_system_status */
osMessageQueueId_t queue_system_statusHandle;
const osMessageQueueAttr_t queue_system_status_attributes = {
  .name = "queue_system_status"
};

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */

/* USER CODE END FunctionPrototypes */

void start_task_audio_capt(void *argument);
void start_task_feature_extr(void *argument);
void start_task_ai_inter(void *argument);
void start_task_result(void *argument);
void start_task_user_inter(void *argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* Create the queue(s) */
  /* creation of queue_audio_process */
  queue_audio_processHandle = osMessageQueueNew (3, sizeof(uint32_t), &queue_audio_process_attributes);

  /* creation of queue_feature_inference */
  queue_feature_inferenceHandle = osMessageQueueNew (2, sizeof(uint32_t), &queue_feature_inference_attributes);

  /* creation of queue_system_status */
  queue_system_statusHandle = osMessageQueueNew (5, sizeof(uint32_t), &queue_system_status_attributes);

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of task_audio_capt */
  task_audio_captHandle = osThreadNew(start_task_audio_capt, NULL, &task_audio_capt_attributes);

  /* creation of task_feature_ex */
  task_feature_exHandle = osThreadNew(start_task_feature_extr, NULL, &task_feature_ex_attributes);

  /* creation of task_ai_inter */
  task_ai_interHandle = osThreadNew(start_task_ai_inter, NULL, &task_ai_inter_attributes);

  /* creation of task_result */
  task_resultHandle = osThreadNew(start_task_result, NULL, &task_result_attributes);

  /* creation of task_user_inter */
  task_user_interHandle = osThreadNew(start_task_user_inter, NULL, &task_user_inter_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

}

/* USER CODE BEGIN Header_start_task_audio_capt */
/**
  * @brief  Function implementing the task_audio_capt thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_start_task_audio_capt */
__weak void start_task_audio_capt(void *argument)
{
  /* USER CODE BEGIN start_task_audio_capt */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END start_task_audio_capt */
}

/* USER CODE BEGIN Header_start_task_feature_extr */
/**
* @brief Function implementing the task_feature_ex thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_start_task_feature_extr */
__weak void start_task_feature_extr(void *argument)
{
  /* USER CODE BEGIN start_task_feature_extr */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END start_task_feature_extr */
}

/* USER CODE BEGIN Header_start_task_ai_inter */
/**
* @brief Function implementing the task_ai_inter thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_start_task_ai_inter */
__weak void start_task_ai_inter(void *argument)
{
  /* USER CODE BEGIN start_task_ai_inter */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END start_task_ai_inter */
}

/* USER CODE BEGIN Header_start_task_result */
/**
* @brief Function implementing the task_result thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_start_task_result */
__weak void start_task_result(void *argument)
{
  /* USER CODE BEGIN start_task_result */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END start_task_result */
}

/* USER CODE BEGIN Header_start_task_user_inter */
/**
* @brief Function implementing the task_user_inter thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_start_task_user_inter */
__weak void start_task_user_inter(void *argument)
{
  /* USER CODE BEGIN start_task_user_inter */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END start_task_user_inter */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */

/* USER CODE END Application */

