import numpy as np
import librosa.feature
import yaml
import os


class FeatureExtractor:
  def __init__(self, config_path='config/config.yaml'):
    # 加载配置
    with open(config_path, 'r') as file:
      self.config = yaml.safe_load(file)

    # 音频参数
    self.sample_rate = self.config['audio']['sample_rate']
    self.n_mfcc = self.config['audio']['n_mfcc']
    self.hop_length = self.config['audio']['hop_length']
    self.n_fft = self.config['audio']['n_fft']

    # 新增音频参数
    self.preemphasis = self.config['audio'].get('preemphasis', 0.97)
    self.window_type = self.config['audio'].get('window_type', 'hann')
    self.use_delta = self.config['audio'].get('use_delta', True)

    # 路径配置
    self.processed_data_path = self.config['paths'].get('processed_data', 'data/processed')
    self.feature_format = self.config['file_naming'].get('feature_format', 'npy')

  def extract_mfcc(self, audio_data):
    """提取MFCC特征"""
    # 应用预加重
    if self.preemphasis > 0:
      audio_data = librosa.effects.preemphasis(audio_data, coef=self.preemphasis)

    # 提取MFCC
    mfccs = librosa.feature.mfcc(
      y=audio_data,
      sr=self.sample_rate,
      n_mfcc=self.n_mfcc,
      hop_length=self.hop_length,
      n_fft=self.n_fft,
      window=self.window_type
    )

    # 标准化MFCC特征
    mfccs = (mfccs - np.mean(mfccs, axis=1, keepdims=True)) / \
            (np.std(mfccs, axis=1, keepdims=True) + 1e-8)

    # 如果不需要增量特征，直接返回MFCC
    if not self.use_delta:
      return mfccs

    # 添加delta特征 (一阶差分)
    delta1 = librosa.feature.delta(mfccs, width=3)

    # 添加delta2特征 (二阶差分)
    delta2 = librosa.feature.delta(mfccs, order=2, width=3)

    # 合并所有特征
    features = np.vstack([mfccs, delta1, delta2])

    return features

  def extract_features(self, audio_data):
    """提取完整的特征集，包括其他潜在特征"""
    # 基础MFCC特征(带可选的delta)
    features = self.extract_mfcc(audio_data)

    # 这里可以添加其他特征提取，如有需要
    # 例如：频谱质心、色谱图等

    return features

  def prepare_for_model(self, features):
    """为模型准备特征输入"""
    # 转置特征，使其形状为 [time_steps, n_features]
    features = features.T

    # 添加批次和通道维度
    # 形状变为 [1, time_steps, n_features, 1]
    features = np.expand_dims(np.expand_dims(features, axis=0), axis=-1)

    return features

  def get_feature_path(self, user_id, filename):
    """根据配置生成特征文件路径"""
    user_dir = os.path.join(self.processed_data_path, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{filename}.{self.feature_format}")

  def save_features(self, features, output_path):
    """保存特征到文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    np.save(output_path, features)
    print(f"特征已保存至: {output_path}")

  def load_features(self, input_path):
    """从文件加载特征"""
    if not os.path.exists(input_path):
      raise FileNotFoundError(f"特征文件不存在: {input_path}")

    features = np.load(input_path)
    return features

  def batch_extract(self, audio_files, user_id):
    """批量提取特征并保存"""
    extracted_features = []

    for i, audio_file in enumerate(audio_files):
      print(f"处理文件 {i + 1}/{len(audio_files)}: {os.path.basename(audio_file)}")

      # 加载音频
      audio_data, sr = librosa.load(audio_file, sr=self.sample_rate)

      # 提取特征
      features = self.extract_features(audio_data)

      # 生成输出文件名
      base_name = os.path.splitext(os.path.basename(audio_file))[0]
      output_path = self.get_feature_path(user_id, base_name)

      # 保存特征
      self.save_features(features, output_path)
      extracted_features.append((output_path, features))

    return extracted_features