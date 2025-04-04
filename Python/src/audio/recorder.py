import pyaudio
import wave
import numpy as np
import os
from datetime import datetime
import yaml


class AudioRecorder:
  def __init__(self, config_path='config/config.yaml'):
    # 加载配置
    with open(config_path, 'r') as file:
      self.config = yaml.safe_load(file)

    self.sample_rate = self.config['audio']['sample_rate']
    self.duration = self.config['audio']['duration']
    self.chunk = 1024
    self.format = pyaudio.paInt16
    self.channels = 1

    # 从配置获取路径和文件格式
    self.raw_data_path = self.config['paths']['raw_data']
    self.audio_format = self.config['file_naming']['audio_format']

  def record_audio(self, output_path=None, user_id=None, sample_num=1):
    """录制音频并保存"""
    if output_path is None:
      if user_id is None:
        user_id = "unknown"

      # 使用配置的文件命名模式
      filename = f"{user_id}_sample{sample_num}.{self.audio_format}"
      output_dir = os.path.join(self.raw_data_path, user_id)
      os.makedirs(output_dir, exist_ok=True)
      output_path = os.path.join(output_dir, filename)

    # 初始化PyAudio
    p = pyaudio.PyAudio()

    print(f"开始录音... (持续 {self.duration} 秒)")

    # 打开音频流
    stream = p.open(format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk)

    frames = []

    # 录制音频
    for i in range(0, int(self.sample_rate / self.chunk * self.duration)):
      data = stream.read(self.chunk)
      frames.append(data)

    print("录音结束")

    # 停止并关闭音频流
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存音频文件
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(self.channels)
    wf.setsampwidth(p.get_sample_size(self.format))
    wf.setframerate(self.sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"音频已保存至: {output_path}")

    return output_path

  def record_samples(self, n_samples=5, output_dir=None, file_prefix="unknown", file_format=None):
    """录制多个音频样本

    Args:
        n_samples: 要录制的样本数
        output_dir: 输出目录
        file_prefix: 文件名前缀(通常是用户ID)
        file_format: 文件格式(扩展名)

    Returns:
        已保存音频文件的路径列表
    """
    file_paths = []

    # 使用提供的参数或配置默认值
    if output_dir is None:
      output_dir = os.path.join(self.raw_data_path, file_prefix)
    if file_format is None:
      file_format = self.audio_format

    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)

    for i in range(n_samples):
      input(f"按Enter开始录制第 {i + 1}/{n_samples} 个样本...")

      # 创建输出文件路径
      filename = f"{file_prefix}_sample{i + 1}.{file_format}"
      file_path = os.path.join(output_dir, filename)

      # 录制并保存
      self.record_audio(output_path=file_path)
      file_paths.append(file_path)

      print(f"样本 {i + 1}/{n_samples} 已保存")

    return file_paths

  def record_multiple(self, user_id, passphrase, n_samples=5, output_dir=None, file_pattern=None, file_format=None):
    """向后兼容的多样本录制方法

    注: 此方法保留以保持与旧代码兼容
    """
    # 默认使用配置的路径
    if output_dir is None:
      output_dir = os.path.join(self.raw_data_path, user_id)
    if file_format is None:
      file_format = self.audio_format

    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)

    file_paths = []
    for i in range(n_samples):
      input(f"按Enter开始录制第 {i + 1}/{n_samples} 个样本...")

      # 创建输出文件路径
      if file_pattern:
        filename = f"{file_pattern.format(phrase=passphrase, sample_num=i + 1)}.{file_format}"
      else:
        filename = f"{passphrase}_{i + 1}.{file_format}"

      file_path = os.path.join(output_dir, filename)

      # 录制并保存
      self.record_audio(output_path=file_path)
      file_paths.append(file_path)

    return file_paths

  def load_audio(self, file_path):
    """从文件加载音频"""
    with wave.open(file_path, 'rb') as wf:
      # 获取音频参数
      sample_rate = wf.getframerate()
      n_frames = wf.getnframes()

      # 读取音频数据
      frames = wf.readframes(n_frames)

    # 将二进制数据转换为numpy数组
    audio_data = np.frombuffer(frames, dtype=np.int16)

    # 将int16转换为float32并标准化到[-1, 1]范围
    audio_data = audio_data.astype(np.float32) / 32768.0

    return audio_data, sample_rate