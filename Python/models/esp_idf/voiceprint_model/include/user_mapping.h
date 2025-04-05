// 自动生成的用户映射头文件
#pragma once

#include <stdint.h>

// 用户ID映射
#define USER_COUNT 5

typedef struct {
    uint8_t id;
    const char* name;
} UserMapping;

extern const UserMapping USER_TABLE[USER_COUNT];
