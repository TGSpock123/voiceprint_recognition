/*
 * audio_capture.h
 *
 *  Created on: Apr 11, 2025
 *      Author: T G Spock
 */

#ifndef INC_AUDIO_CAPTURE_H_
#define INC_AUDIO_CAPTURE_H_

/* 音频配置参数 */
#define AUDIO_SAMPLE_RATE     16000   // 16kHz采样率
#define AUDIO_DURATION_SEC    3       // 3秒缓冲区
#define AUDIO_BUFFER_SAMPLES  (AUDIO_SAMPLE_RATE * AUDIO_DURATION_SEC)
#define DMA_BUFFER_SIZE 4

/* 音频采集状态 */
typedef enum {
    AUDIO_STATE_IDLE,         // 空闲状态，等待触发
    AUDIO_STATE_CAPTURING,    // 正在采集
    AUDIO_STATE_PROCESSING    // 正在处理
} AudioState_t;

extern volatile uint32_t currentSampleIndex;  // 当前样本索引
extern volatile AudioState_t audioState;  // 当前状态
extern volatile uint8_t captureDoneFlag;      // 采集完成标志
extern int32_t audioBuffer[AUDIO_BUFFER_SAMPLES];

/* 函数声明 */
void AudioCapture_Init(void);
void AudioCapture_Start(void);
void AudioCapture_Stop(void);
void ProcessAllAudioData(void);

#endif /* INC_AUDIO_CAPTURE_H_ */
