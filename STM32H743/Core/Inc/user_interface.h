/*
 * user_interface.h
 *
 *  Created on: Apr 9, 2025
 *      Author: T G Spock
 */

#ifndef INC_USER_INTERFACE_H_
#define INC_USER_INTERFACE_H_

#include "main.h"
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"
#include "queue.h"

// 用户命令结构
typedef enum {
  CMD_ENROLL_USER,
  CMD_VERIFY_USER,
  CMD_DELETE_USER,
  CMD_SYSTEM_RESET
} command_type_t;

typedef struct {
  command_type_t type;
  uint8_t userId;
  void* additionalData;
} user_command_t;

#endif /* INC_USER_INTERFACE_H_ */
