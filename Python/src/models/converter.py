import os
import numpy as np
import tensorflow as tf
import argparse
import yaml
import sys

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def convert_to_tflite(model_path, output_dir, config_path, quantize=True, representative_dataset=None):
  """将模型转换为TFLite格式并生成ESP-IDF兼容文件"""

  # 加载配置
  with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

  print(f"加载模型: {model_path}")
  # 加载已保存的编码器模型
  model = tf.keras.models.load_model(model_path)

  # 创建TFLite转换器
  converter = tf.lite.TFLiteConverter.from_keras_model(model)

  # 优化设置
  converter.optimizations = [tf.lite.Optimize.DEFAULT]

  # 如果需要量化
  if quantize:
    if representative_dataset is not None:
      # 全整数量化需要代表性数据集
      print("应用整数量化...")
      converter.representative_dataset = representative_dataset
      converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
      converter.inference_input_type = tf.int8
      converter.inference_output_type = tf.int8
    else:
      # 后训练动态范围量化
      print("应用动态范围量化...")

  # 转换模型
  print("转换模型中...")
  tflite_model = converter.convert()

  # 创建ESP-IDF组件目录结构
  component_dir = os.path.join(output_dir, "voiceprint_model")
  include_dir = os.path.join(component_dir, "include")
  os.makedirs(include_dir, exist_ok=True)

  # 保存TFLite模型文件
  tflite_path = os.path.join(component_dir, "voiceprint_model.tflite")
  with open(tflite_path, 'wb') as f:
    f.write(tflite_model)

  # 获取模型大小信息
  model_size_kb = os.path.getsize(tflite_path) / 1024
  print(f"模型转换完成，大小: {model_size_kb:.2f} KB")

  # 创建模型头文件
  model_header_path = os.path.join(include_dir, "voiceprint_model.h")
  with open(model_header_path, 'w') as f:
    f.write("// 自动生成的模型头文件\n")
    f.write("#pragma once\n\n")
    f.write("#include <stdint.h>\n\n")
    f.write("// 模型字节数组\n")
    f.write("extern const unsigned char voiceprint_model[];\n")
    f.write("extern const unsigned int voiceprint_model_len;\n")

  # 创建模型C源文件
  model_source_path = os.path.join(component_dir, "voiceprint_model.c")
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

  # 加载用户映射
  try:
    user_mapping = np.load(os.path.join(config['paths']['models_dir'], 'user_mapping.npy'),
                           allow_pickle=True).item()
  except:
    user_mapping = {"0": "Unknown"}  # 默认用户映射
    print("警告：未找到用户映射文件，使用默认映射")

  # 创建用户映射头文件
  user_header_path = os.path.join(include_dir, "user_mapping.h")
  with open(user_header_path, 'w') as f:
    f.write("// 自动生成的用户映射头文件\n")
    f.write("#pragma once\n\n")
    f.write("#include <stdint.h>\n\n")
    f.write("// 用户ID映射\n")
    f.write(f"#define USER_COUNT {len(user_mapping)}\n\n")
    f.write("typedef struct {\n")
    f.write("  uint8_t id;\n")
    f.write("  const char* name;\n")
    f.write("} UserMapping;\n\n")
    f.write("extern const UserMapping USER_TABLE[USER_COUNT];\n")

  # 创建用户映射C源文件
  user_source_path = os.path.join(component_dir, "user_mapping.c")
  with open(user_source_path, 'w') as f:
    f.write("// 自动生成的用户映射实现文件\n")
    f.write("#include \"user_mapping.h\"\n\n")
    f.write("const UserMapping USER_TABLE[USER_COUNT] = {\n")
    for user_id, user_name in user_mapping.items():
      f.write(f"  {{{user_id}, \"{user_name}\"}},\n")
    f.write("};\n")

  # 创建配置头文件
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

  # 创建CMakeLists.txt
  cmake_path = os.path.join(component_dir, "CMakeLists.txt")
  with open(cmake_path, 'w') as f:
    f.write("# 自动生成的CMakeLists.txt\n\n")
    f.write("idf_component_register(SRCS \"voiceprint_model.c\" \"user_mapping.c\"\n")
    f.write("                       INCLUDE_DIRS \"include\"\n")
    f.write("                       REQUIRES \"esp_common\")\n")

  print(f"已生成所有必要的文件到: {component_dir}")
  return component_dir


def generate_representative_dataset(config_path, num_samples=100):
  """生成代表性数据集用于量化"""
  # 这里应该加载一些已处理的特征样本
  from src.utils.data_loader import VoiceprintDataLoader

  data_loader = VoiceprintDataLoader(config_path=config_path)
  features, _, _ = data_loader.load_features()

  # 限制样本数量
  if len(features) > num_samples:
    indices = np.random.choice(len(features), num_samples, replace=False)
    features = features[indices]

  def representative_dataset():
    for feature in features:
      # 扩展batch维度
      feature = np.expand_dims(feature, axis=0)
      yield [feature.astype(np.float32)]

  return representative_dataset


def main():
  parser = argparse.ArgumentParser(description='将声纹识别模型转换为ESP-IDF兼容格式')
  parser.add_argument('--config', type=str, default='config/config.yaml', help='配置文件路径')
  parser.add_argument('--model', type=str, help='要转换的模型路径')
  parser.add_argument('--output', type=str, help='输出目录路径')
  parser.add_argument('--no-quantize', action='store_true', help='禁用量化')
  args = parser.parse_args()

  # 加载配置
  with open(args.config, 'r') as file:
    config = yaml.safe_load(file)

  # 设置默认路径
  if args.model is None:
    args.model = os.path.join(config['paths']['models_dir'], 'encoder_model.keras')

  if args.output is None:
    args.output = os.path.join(config['paths']['models_dir'], 'esp_idf')

  # 判断是否执行量化
  quantize = not args.no_quantize and config['tflite'].get('quantization', True)

  # 如果需要量化，生成代表性数据集
  representative_dataset = None
  if quantize:
    rep_dataset_size = config['tflite'].get('representative_dataset_size', 100)
    print(f"生成代表性数据集 ({rep_dataset_size}个样本)...")
    representative_dataset = generate_representative_dataset(args.config, rep_dataset_size)

  # 转换模型
  output_dir = convert_to_tflite(
    args.model,
    args.output,
    args.config,
    quantize=quantize,
    representative_dataset=representative_dataset
  )

  print(f"\nESP-IDF组件已生成在: {output_dir}")
  print("\n使用方法:")
  print("1. 将整个voiceprint_model目录复制到您的ESP-IDF项目的components目录下")
  print("2. 在项目的CMakeLists.txt中确保EXTRA_COMPONENT_DIRS包含此组件")
  print("3. 在您的代码中包含以下头文件:")
  print("   #include \"voiceprint_model.h\"")
  print("   #include \"voiceprint_config.h\"")
  print("   #include \"user_mapping.h\"")


if __name__ == "__main__":
  main()