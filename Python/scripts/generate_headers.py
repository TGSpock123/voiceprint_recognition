import os
import yaml
import numpy as np

def generate_headers(tflite_path, include_dir, config_path):
    """生成ESP32-S3所需的头文件"""
    
    # 确保include目录存在
    os.makedirs(include_dir, exist_ok=True)
    
    # 1. 生成 voiceprint_model.h
    model_header_path = os.path.join(include_dir, "voiceprint_model.h")
    with open(model_header_path, 'w') as f:
        f.write("// 自动生成的模型头文件\n")
        f.write("#pragma once\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write("// 模型字节数组\n")
        f.write("extern const unsigned char voiceprint_model[];\n")
        f.write("extern const unsigned int voiceprint_model_len;\n")
    
    # 读取配置文件
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # 2. 生成 voiceprint_config.h
    config_header_path = os.path.join(include_dir, "voiceprint_config.h")
    with open(config_header_path, 'w') as f:
        f.write("// ESP32声纹识别配置\n")
        f.write("#pragma once\n\n")
        f.write("#include <stdint.h>\n\n")
        
        # 音频参数
        f.write(f"#define SAMPLE_RATE {config['audio']['sample_rate']}\n")
        f.write(f"#define AUDIO_LENGTH {int(config['audio']['duration'] * config['audio']['sample_rate'])}\n")
        f.write(f"#define MFCC_FEATURES {config['audio']['n_mfcc']}\n")
        
        if config['audio'].get('use_delta', False):
            f.write("#define USE_DELTA 1\n")
        else:
            f.write("#define USE_DELTA 0\n")
        
        # 特征提取参数
        f.write(f"#define FFT_SIZE {config['audio']['n_fft']}\n")
        f.write(f"#define HOP_LENGTH {config['audio']['hop_length']}\n")
        f.write(f"#define PREEMPHASIS_COEF {config['audio']['preemphasis']:.6f}f\n")
        
        # 模型参数
        f.write(f"#define INPUT_HEIGHT {config['model']['input_shape'][1]}\n")
        f.write(f"#define INPUT_WIDTH {config['model']['input_shape'][2]}\n")
        f.write(f"#define INPUT_CHANNELS {config['model']['input_shape'][3]}\n")
        f.write(f"#define EMBEDDING_DIM {config['model']['embedding_dim']}\n")
        f.write(f"#define SIMILARITY_THRESHOLD {config['verification']['similarity_threshold']:.6f}f\n")
        
        # ESP32特定参数
        f.write(f"#define INPUT_BUFFER_SIZE {config['esp32']['input_buffer_size']}\n")
        f.write(f"#define WAKE_WORD_TIMEOUT_MS {config['esp32']['wake_word_timeout'] * 1000}\n")
        f.write(f"#define LOW_POWER_DELAY_MS {config['esp32']['low_power_delay'] * 1000}\n")
    
    # 3. 生成 user_mapping.h
    try:
        user_mapping = np.load(os.path.join(config['paths']['models_dir'], 'user_mapping.npy'),
                             allow_pickle=True).item()
    except:
        user_mapping = {"0": "Unknown"}
        print("警告：未找到用户映射文件，使用默认映射")
    
    user_header_path = os.path.join(include_dir, "user_mapping.h")
    with open(user_header_path, 'w') as f:
        f.write("// 自动生成的用户映射头文件\n")
        f.write("#pragma once\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write("// 用户ID映射\n")
        f.write(f"#define USER_COUNT {len(user_mapping)}\n\n")
        f.write("typedef struct {\n")
        f.write("    uint8_t id;\n")
        f.write("    const char* name;\n")
        f.write("} UserMapping;\n\n")
        f.write("extern const UserMapping USER_TABLE[USER_COUNT];\n")
    
    # 生成对应的C文件
    model_source_path = os.path.join(os.path.dirname(include_dir), "voiceprint_model.c")
    with open(model_source_path, 'w') as f:
        f.write("// 自动生成的模型实现文件\n")
        f.write("#include \"voiceprint_model.h\"\n\n")
        f.write("// 模型字节数组\n")
        f.write("const unsigned char voiceprint_model[] = {\n  ")
        
        with open(tflite_path, 'rb') as model_file:
            data = model_file.read()
            for i, byte in enumerate(data):
                f.write(f"0x{byte:02x},")
                if (i + 1) % 12 == 0:
                    f.write("\n  ")
                else:
                    f.write(" ")
        
        f.write("\n};\n\n")
        f.write(f"const unsigned int voiceprint_model_len = {len(data)};\n")
    
    user_source_path = os.path.join(os.path.dirname(include_dir), "user_mapping.c")
    with open(user_source_path, 'w') as f:
        f.write("// 自动生成的用户映射实现文件\n")
        f.write("#include \"user_mapping.h\"\n\n")
        f.write("const UserMapping USER_TABLE[USER_COUNT] = {\n")
        for user_id, user_name in user_mapping.items():
            f.write(f"    {{{user_id}, \"{user_name}\"}},\n")
        f.write("};\n")

    print("头文件生成完成！")
    print(f"生成的文件位置：{include_dir}")
    print("生成的文件包括：")
    print("- voiceprint_model.h")
    print("- voiceprint_config.h")
    print("- user_mapping.h")
    print("- voiceprint_model.c")
    print("- user_mapping.c")

if __name__ == "__main__":
    # 设置路径
    tflite_path = "models/esp_idf/voiceprint_model/voiceprint_model.tflite"
    include_dir = "models/esp_idf/voiceprint_model/include"
    config_path = "config/config.yaml"
    
    # 生成头文件
    generate_headers(tflite_path, include_dir, config_path)