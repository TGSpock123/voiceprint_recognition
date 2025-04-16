#include "audio_processing.h"
#include "esp_driver_i2s.h"
#include "esp_log.h"
#include "esp_dsp.h"
#include "dsps_fft2r.h"
#include "dsps_wind.h"
#include "dsps_view.h"
#include "math.h"

#define TAG "AUDIO_PROC"
#define I2S_NUM I2S_NUM_0
#define SAMPLE_RATE 16000
#define BUFFER_SIZE 16000  // 1秒音频

// MFCC参数
#define FRAME_SIZE 400     // 25ms (16000Hz时)
#define FRAME_STEP 160     // 10ms (16000Hz时)
#define FFT_SIZE 512       // 2的幂次方，足以容纳FRAME_SIZE
#define NUM_FRAMES 94      // 对应模型输入宽度
#define NUM_FILTERS 39     // 对应模型输入高度
#define NUM_MFCC 39        // MFCC特征数量

// 预加重系数
#define PRE_EMPHASIS 0.97f

// FFT工作缓冲区
float *fft_buffer;
float *window_func;
float *mel_filters[NUM_FILTERS];
float *dct_matrix;

// Mel滤波器中心频率
float mel_filter_centers[NUM_FILTERS+2];

// 初始化特征提取所需资源
void initFeatureExtraction() {
    ESP_LOGI(TAG, "初始化特征提取资源");
    
    // 分配FFT和窗函数内存
    fft_buffer = (float*)heap_caps_malloc(FFT_SIZE * 2 * sizeof(float), MALLOC_CAP_8BIT);
    window_func = (float*)heap_caps_malloc(FRAME_SIZE * sizeof(float), MALLOC_CAP_8BIT);
    
    // 创建Hamming窗函数
    dsps_wind_hann_f32(window_func, FRAME_SIZE);
    
    // 初始化FFT
    dsps_fft2r_init_fc32(NULL, FFT_SIZE);
    
    // 创建Mel滤波器组
    
    // 计算Mel刻度
    float mel_low = 2595.0f * log10f(1.0f + 0.0f / 700.0f);
    float mel_high = 2595.0f * log10f(1.0f + (SAMPLE_RATE / 2.0f) / 700.0f);
    
    // 计算Mel滤波器中心频率
    for (int i = 0; i < NUM_FILTERS + 2; i++) {
        float mel = mel_low + i * (mel_high - mel_low) / (NUM_FILTERS + 1);
        mel_filter_centers[i] = 700.0f * (powf(10.0f, mel / 2595.0f) - 1.0f);
    }
    
    // 为每个滤波器分配内存并初始化
    for (int i = 0; i < NUM_FILTERS; i++) {
        mel_filters[i] = (float*)heap_caps_calloc(FFT_SIZE/2, sizeof(float), MALLOC_CAP_8BIT);
        
        // 设置三角滤波器
        float f_m_minus = mel_filter_centers[i];
        float f_m = mel_filter_centers[i+1];
        float f_m_plus = mel_filter_centers[i+2];
        
        // 转换为FFT bin索引
        int bin_m_minus = (int)floorf(f_m_minus * FFT_SIZE / SAMPLE_RATE);
        int bin_m = (int)floorf(f_m * FFT_SIZE / SAMPLE_RATE);
        int bin_m_plus = (int)floorf(f_m_plus * FFT_SIZE / SAMPLE_RATE);
        
        // 设置上升边
        for (int j = bin_m_minus; j < bin_m; j++) {
            if (j >= 0 && j < FFT_SIZE/2) {
                mel_filters[i][j] = (j - bin_m_minus) / (float)(bin_m - bin_m_minus);
            }
        }
        
        // 设置下降边
        for (int j = bin_m; j < bin_m_plus; j++) {
            if (j >= 0 && j < FFT_SIZE/2) {
                mel_filters[i][j] = (bin_m_plus - j) / (float)(bin_m_plus - bin_m);
            }
        }
    }
    
    // 创建DCT矩阵
    dct_matrix = (float*)heap_caps_malloc(NUM_FILTERS * NUM_MFCC * sizeof(float), MALLOC_CAP_8BIT);
    
    for (int i = 0; i < NUM_MFCC; i++) {
        for (int j = 0; j < NUM_FILTERS; j++) {
            dct_matrix[i * NUM_FILTERS + j] = cosf(M_PI * i * (j + 0.5f) / NUM_FILTERS);
        }
    }
    
    ESP_LOGI(TAG, "特征提取资源初始化完成");
}

// 释放资源
void deinitFeatureExtraction() {
    heap_caps_free(fft_buffer);
    heap_caps_free(window_func);
    
    for (int i = 0; i < NUM_FILTERS; i++) {
        heap_caps_free(mel_filters[i]);
    }
    
    heap_caps_free(dct_matrix);
}

void initializeAudio() {
    // I2S配置代码保持不变
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = false
    };

    i2s_pin_config_t pin_config = {
        .mck_io_num = I2S_PIN_NO_CHANGE,
        .bck_io_num = 41,    // 根据您的硬件连接调整
        .ws_io_num = 42,     // 根据您的硬件连接调整
        .data_in_num = 2,    // 根据您的硬件连接调整
        .data_out_num = I2S_PIN_NO_CHANGE
    };

    ESP_ERROR_CHECK(i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL));
    ESP_ERROR_CHECK(i2s_set_pin(I2S_NUM, &pin_config));
    
    // 初始化特征提取
    initFeatureExtraction();
}

bool captureAndExtractFeatures(int8_t* feature_data) {
    int16_t raw_samples[BUFFER_SIZE];
    size_t bytes_read = 0;
    
    // 录制原始音频
    ESP_LOGI(TAG, "开始录制音频...");
    esp_err_t ret = i2s_read(I2S_NUM, raw_samples, sizeof(raw_samples), &bytes_read, portMAX_DELAY);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "音频录制失败");
        return false;
    }
    
    // 计算实际样本数
    int num_samples = bytes_read / sizeof(int16_t);
    ESP_LOGI(TAG, "录制了 %d 个样本", num_samples);
    
    // 预加重处理
    float preemphasized[BUFFER_SIZE];
    preemphasized[0] = raw_samples[0] / 32768.0f;
    for (int i = 1; i < num_samples; i++) {
        preemphasized[i] = raw_samples[i] / 32768.0f - PRE_EMPHASIS * (raw_samples[i-1] / 32768.0f);
    }
    
    // 分帧、加窗、FFT、梅尔滤波和MFCC计算
    float mel_energies[NUM_FRAMES][NUM_FILTERS];
    
    // 对每个帧进行处理
    for (int frame = 0; frame < NUM_FRAMES; frame++) {
        int frame_start = frame * FRAME_STEP;
        
        // 检查是否有足够的样本
        if (frame_start + FRAME_SIZE > num_samples) {
            ESP_LOGE(TAG, "样本不足，需要更长的录音");
            return false;
        }
        
        // 清零FFT缓冲区
        memset(fft_buffer, 0, FFT_SIZE * 2 * sizeof(float));
        
        // 应用窗函数并填充FFT缓冲区
        for (int i = 0; i < FRAME_SIZE; i++) {
            fft_buffer[2*i] = preemphasized[frame_start + i] * window_func[i];
            fft_buffer[2*i+1] = 0.0f;  // 虚部为0
        }
        
        // 执行FFT
        dsps_fft2r_fc32(fft_buffer, FFT_SIZE);
        
        // 计算功率谱
        float power_spectrum[FFT_SIZE/2];
        for (int i = 0; i < FFT_SIZE/2; i++) {
            float real = fft_buffer[2*i];
            float imag = fft_buffer[2*i+1];
            power_spectrum[i] = (real * real + imag * imag) / FFT_SIZE;
        }
        
        // 应用Mel滤波器组
        for (int j = 0; j < NUM_FILTERS; j++) {
            float mel_energy = 0.0f;
            for (int i = 0; i < FFT_SIZE/2; i++) {
                mel_energy += power_spectrum[i] * mel_filters[j][i];
            }
            
            // 计算对数能量，避免取log(0)
            mel_energies[frame][j] = mel_energy > 1e-10f ? logf(mel_energy) : logf(1e-10f);
        }
    }
    
    // 执行DCT计算MFCC
    float mfcc_features[NUM_FRAMES][NUM_MFCC];
    for (int frame = 0; frame < NUM_FRAMES; frame++) {
        for (int i = 0; i < NUM_MFCC; i++) {
            float sum = 0.0f;
            for (int j = 0; j < NUM_FILTERS; j++) {
                sum += mel_energies[frame][j] * dct_matrix[i * NUM_FILTERS + j];
            }
            mfcc_features[frame][i] = sum;
        }
    }
    
    // 归一化MFCC特征（简单均值方差归一化）
    float mean = 0.0f, var = 0.0f;
    int total_features = NUM_FRAMES * NUM_MFCC;
    
    // 计算均值
    for (int f = 0; f < NUM_FRAMES; f++) {
        for (int m = 0; m < NUM_MFCC; m++) {
            mean += mfcc_features[f][m];
        }
    }
    mean /= total_features;
    
    // 计算方差
    for (int f = 0; f < NUM_FRAMES; f++) {
        for (int m = 0; m < NUM_MFCC; m++) {
            float diff = mfcc_features[f][m] - mean;
            var += diff * diff;
        }
    }
    var /= total_features;
    float std_dev = sqrtf(var);
    
    // 归一化特征
    for (int f = 0; f < NUM_FRAMES; f++) {
        for (int m = 0; m < NUM_MFCC; m++) {
            mfcc_features[f][m] = (mfcc_features[f][m] - mean) / (std_dev + 1e-10f);
        }
    }
    
    // 量化为INT8格式
    // 量化参数从模型分析中获得
    float scale = 0.050155963748693466;
    int zero_point = -3;
    
    // 将特征量化为INT8并填充模型输入
    for (int f = 0; f < NUM_FRAMES; f++) {
        for (int m = 0; m < NUM_MFCC; m++) {
            // 计算量化后的值: (float_val / scale) + zero_point
            float quantized_value = (mfcc_features[f][m] / scale) + zero_point;
            
            // 截断到INT8范围 [-128, 127]
            if (quantized_value > 127.0f) quantized_value = 127.0f;
            if (quantized_value < -128.0f) quantized_value = -128.0f;
            
            // 填充模型输入，确保格式为[1, 39, 94, 1]
            feature_data[m * NUM_FRAMES + f] = (int8_t)quantized_value;
        }
    }
    
    ESP_LOGI(TAG, "特征提取完成");
    return true;
}