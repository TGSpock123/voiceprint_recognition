import numpy as np
import librosa
import yaml

class AudioProcessor:
  def __init__(self, config_path='config/config.yaml'):
    # 加载配置
    with open(config_path, 'r') as file:
      config = yaml.safe_load(file)

    self.sample_rate = config['audio']['sample_rate']
    self.duration = config['audio']['duration']

  def normalize_audio(self, audio_data):
    """对音频进行归一化"""
    # 确保音频是浮点数类型
    if audio_data.dtype != np.float32:
      audio_data = audio_data.astype(np.float32)

    # 归一化到 [-1, 1] 范围
    if np.max(np.abs(audio_data)) > 0:
      audio_data = audio_data / np.max(np.abs(audio_data))

    return audio_data

  def trim_silence(self, audio_data, threshold=0.01):
    """裁剪静音部分"""
    # 使用librosa的trim函数裁剪静音
    trimmed_audio, _ = librosa.effects.trim(audio_data, top_db=20)
    return trimmed_audio

  def resample(self, audio_data, orig_sr, target_sr=None):
    """重采样音频"""
    if target_sr is None:
      target_sr = self.sample_rate

    if orig_sr != target_sr:
      audio_data = librosa.resample(audio_data, orig_sr=orig_sr, target_sr=target_sr)

    return audio_data

  def adjust_length(self, audio_data):
    """调整音频长度"""
    target_length = int(self.sample_rate * self.duration)

    if len(audio_data) > target_length:
      # 裁剪
      audio_data = audio_data[:target_length]
    elif len(audio_data) < target_length:
      # 用0填充
      padding = np.zeros(target_length - len(audio_data))
      audio_data = np.concatenate([audio_data, padding])

    return audio_data

  def preprocess_audio(self, audio_data, orig_sr=None):
    """音频预处理完整流程"""
    # 确定采样率
    if orig_sr is None:
      orig_sr = self.sample_rate

    # 归一化
    audio_data = self.normalize_audio(audio_data)

    # 裁剪静音
    audio_data = self.trim_silence(audio_data)

    # 重采样
    audio_data = self.resample(audio_data, orig_sr)

    # 调整长度
    audio_data = self.adjust_length(audio_data)

    return audio_data

  def apply_augmentation(self, audio_data):
    """应用数据增强技术"""
    augmented_data = audio_data.copy()

    # 随机选择一种增强方法
    augmentation_type = np.random.choice(['noise', 'shift', 'speed', 'pitch'])

    if augmentation_type == 'noise':
      # 添加随机噪声
      noise_level = np.random.uniform(0.001, 0.01)
      noise = np.random.normal(0, noise_level, len(augmented_data))
      augmented_data = augmented_data + noise
      augmented_data = np.clip(augmented_data, -1, 1)

    elif augmentation_type == 'shift':
      # 时间偏移
      shift_amount = int(np.random.uniform(-0.1, 0.1) * len(augmented_data))
      augmented_data = np.roll(augmented_data, shift_amount)

    elif augmentation_type == 'speed':
      # 速度微调
      speed_factor = np.random.uniform(0.9, 1.1)
      augmented_data = librosa.effects.time_stretch(augmented_data, rate=speed_factor)
      augmented_data = self.adjust_length(augmented_data)

    elif augmentation_type == 'pitch':
      # 音调微调
      n_steps = np.random.uniform(-1, 1)
      augmented_data = librosa.effects.pitch_shift(augmented_data, sr=self.sample_rate, n_steps=n_steps)

    return augmented_data