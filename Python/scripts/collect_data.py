import os
import argparse
import sys
import yaml

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio.recorder import AudioRecorder
from src.audio.processor import AudioProcessor
from src.features.extractor import FeatureExtractor


def main():
  parser = argparse.ArgumentParser(description='声纹数据收集工具')
  parser.add_argument('--user_id', type=str, required=True, help='用户ID')
  parser.add_argument('--samples', type=int, default=30, help='每个用户采集的样本数')
  parser.add_argument('--config', type=str, default='config/config.yaml', help='配置文件路径')
  args = parser.parse_args()

  # 加载配置
  with open(args.config, 'r') as file:
    config = yaml.safe_load(file)

  # 初始化组件
  recorder = AudioRecorder(config_path=args.config)
  processor = AudioProcessor(config_path=args.config)
  extractor = FeatureExtractor(config_path=args.config)

  print(f"\n开始为用户 {args.user_id} 收集声纹数据...")
  print(f"采集样本数: {args.samples}")
  print("\n请按照指示在安静环境中录制您的声音")
  print("重要提示: 请在每次录音时说出相同的解锁词句")

  # 从配置中获取路径
  raw_dir = os.path.join(config['paths']['raw_data'], args.user_id)
  processed_dir = os.path.join(config['paths']['processed_data'], args.user_id)
  os.makedirs(raw_dir, exist_ok=True)
  os.makedirs(processed_dir, exist_ok=True)

  # 获取文件命名规则
  sample_pattern = config['file_naming']['sample_pattern']
  audio_format = config['file_naming']['audio_format']
  feature_format = config['file_naming']['feature_format']

  # 录制音频
  audio_files = recorder.record_samples(
    n_samples=args.samples,
    output_dir=raw_dir,
    file_prefix=args.user_id,
    file_format=audio_format
  )

  # 处理和提取特征
  for i, audio_file in enumerate(audio_files):
    print(f"\n处理样本 {i + 1}/{len(audio_files)}...")

    # 加载音频
    audio_data, sample_rate = recorder.load_audio(audio_file)

    # 处理音频
    audio_data = processor.normalize_audio(audio_data)
    processed_audio = processor.preprocess_audio(audio_data, sample_rate)

    # 提取特征
    features = extractor.extract_mfcc(processed_audio)

    # 生成特征文件名
    sample_num = i + 1
    filename = f"{args.user_id}_sample{sample_num}"  # 简化命名
    feature_file = os.path.join(processed_dir, f"{filename}.{feature_format}")

    # 保存特征
    extractor.save_features(features, feature_file)

  print("\n数据收集完成！")
  print(f"原始音频保存在: {raw_dir}")
  print(f"处理后的特征保存在: {processed_dir}")


if __name__ == "__main__":
  main()