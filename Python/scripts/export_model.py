import os
import argparse
import yaml
import sys
import numpy as np
import tensorflow as tf

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 启用不安全反序列化
tf.keras.config.enable_unsafe_deserialization()


def l2_normalize(x):
  return tf.nn.l2_normalize(x, axis=1)


def reduce_mean_lambda(x):
  return tf.reduce_mean(x, axis=-1, keepdims=True)


def reduce_max_lambda(x):
  return tf.reduce_max(x, axis=-1, keepdims=True)


def convert_to_tflite(model_path, output_dir, config_path, quantize=True, representative_dataset=None):
  """将模型转换为TFLite格式并生成ESP-IDF兼容文件"""

  # 加载配置
  with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

  print(f"加载模型: {model_path}")

  # 定义所有自定义层的映射
  custom_objects = {
    'l2_normalize_lambda': tf.keras.layers.Lambda(l2_normalize),
    'reduce_mean_lambda': tf.keras.layers.Lambda(reduce_mean_lambda),
    'reduce_max_lambda': tf.keras.layers.Lambda(reduce_max_lambda),
  }

  try:
    # 尝试直接加载模型
    model = tf.keras.models.load_model(
      model_path,
      custom_objects=custom_objects,
      compile=False
    )
  except Exception as e:
    print(f"直接加载失败: {str(e)}")
    print("尝试重建模型...")

    # 从架构文件重建模型
    from src.models.architecture import get_siamese_model
    _, model = get_siamese_model(config_path)
    model.load_weights(model_path)

  print("模型加载成功，准备转换...")

  # 创建TFLite转换器
  converter = tf.lite.TFLiteConverter.from_keras_model(model)

  # 基本设置
  converter.optimizations = [tf.lite.Optimize.DEFAULT]
  converter.allow_custom_ops = True
  converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
    tf.lite.OpsSet.SELECT_TF_OPS
  ]

  # 如果需要量化
  if quantize and representative_dataset is not None:
    print("应用整数量化...")
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
  else:
    print("使用浮点模型...")

  # 转换模型
  print("转换模型中...")
  try:
    tflite_model = converter.convert()
    print("模型转换成功！")
  except Exception as e:
    print(f"转换失败: {str(e)}")
    print("尝试降级转换设置...")
    # 如果转换失败，尝试最基本的设置
    converter.optimizations = []
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
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

  # [生成其他文件的代码保持不变...]

  return component_dir


def generate_representative_dataset(data_dir, num_samples=100):
  """生成代表性数据集用于量化"""
  features = []

  # 获取所有特征文件
  feature_files = []
  for root, _, files in os.walk(data_dir):
    for file in files:
      if file.endswith('.npy'):
        feature_files.append(os.path.join(root, file))

  if len(feature_files) > 0:
    sample_size = min(num_samples, len(feature_files))
    selected_files = np.random.choice(feature_files, sample_size, replace=False)

    for file_path in selected_files:
      feature = np.load(file_path)
      features.append(feature)

    print(f"已加载 {len(features)} 个样本作为代表性数据集")

    def representative_dataset_gen():
      for data in features:
        # 确保形状正确
        if len(data.shape) == 2:
          data = np.expand_dims(data, axis=-1)
        data = np.expand_dims(data, axis=0)  # 添加 batch 维度
        yield [data.astype(np.float32)]

    return representative_dataset_gen

  return None

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
    processed_data_dir = config['paths']['processed_data']
    representative_dataset = generate_representative_dataset(processed_data_dir, rep_dataset_size)

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