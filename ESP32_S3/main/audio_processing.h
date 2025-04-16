#pragma once

#include <stdint.h>

// 输入尺寸应符合模型要求 [1,39,94,1]
#define AUDIO_FEATURE_HEIGHT 39
#define AUDIO_FEATURE_WIDTH 94

/**
 * 从麦克风捕获音频并提取特征
 * @param feature_data 输出的特征数据 (已量化为int8_t格式)
 * @return 成功返回true，否则false
 */
bool captureAndExtractFeatures(int8_t* feature_data);

/**
 * 初始化音频硬件和特征提取资源
 */
void initializeAudio();

/**
 * 释放特征提取资源
 */
void deinitFeatureExtraction();