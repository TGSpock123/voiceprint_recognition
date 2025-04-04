import os
import numpy as np
import yaml
import glob
from sklearn.model_selection import train_test_split


class VoiceprintDataLoader:
  """声纹数据加载器"""

  def __init__(self, config_path='config/config.yaml'):
    """初始化数据加载器

    Args:
        config_path: 配置文件路径
    """
    # 加载配置
    with open(config_path, 'r') as file:
      self.config = yaml.safe_load(file)

    # 设置路径
    self.raw_data_path = self.config['paths']['raw_data']
    self.processed_data_path = self.config['paths']['processed_data']

    # 文件格式
    self.audio_format = self.config['file_naming']['audio_format']
    self.feature_format = self.config['file_naming']['feature_format']

  def get_user_list(self):
    """获取所有用户列表"""
    if not os.path.exists(self.processed_data_path):
      return []

    return [d for d in os.listdir(self.processed_data_path)
            if os.path.isdir(os.path.join(self.processed_data_path, d))]

  def load_features(self):
    """加载所有用户的特征数据

    Returns:
        features: 特征数组
        labels: 标签数组
        user_mapping: 用户ID到标签索引的映射
    """
    features = []
    labels = []
    user_dirs = self.get_user_list()
    user_mapping = {i: user_id for i, user_id in enumerate(user_dirs)}

    for i, user_id in enumerate(user_dirs):
      user_dir = os.path.join(self.processed_data_path, user_id)
      feature_files = glob.glob(os.path.join(user_dir, f"*.{self.feature_format}"))

      for file_path in feature_files:
        feature = np.load(file_path)
        features.append(feature)
        labels.append(i)  # 使用用户索引作为标签

    return np.array(features), np.array(labels), user_mapping

  def split_dataset(self, features, labels):
    """划分数据集为训练、验证和测试集

    Args:
        features: 特征数组
        labels: 标签数组

    Returns:
        训练、验证和测试数据集
    """
    train_ratio = self.config['data']['train_test_split']
    val_ratio = self.config['data']['validation_split']

    # 先划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
      features, labels, test_size=(1 - train_ratio), random_state=42, stratify=labels
    )

    # 再从训练集划分验证集
    if val_ratio > 0:
      val_size = val_ratio / train_ratio
      X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=val_size, random_state=42, stratify=y_train
      )
      return X_train, y_train, X_val, y_val, X_test, y_test
    else:
      return X_train, y_train, None, None, X_test, y_test

  def get_raw_audio_path(self, user_id, phrase, sample_num):
    """获取原始音频文件路径"""
    pattern = self.config['file_naming']['sample_pattern']
    filename = pattern.format(phrase=phrase, sample_num=sample_num)
    return os.path.join(self.raw_data_path, user_id, f"{filename}.{self.audio_format}")

  def get_feature_path(self, user_id, phrase, sample_num):
    """获取特征文件路径"""
    pattern = self.config['file_naming']['sample_pattern']
    filename = pattern.format(phrase=phrase, sample_num=sample_num)
    return os.path.join(self.processed_data_path, user_id, f"{filename}.{self.feature_format}")

  def check_data_integrity(self):
    """检查数据完整性"""
    user_dirs = self.get_user_list()
    issues = []

    for user_id in user_dirs:
      user_dir = os.path.join(self.processed_data_path, user_id)
      feature_files = glob.glob(os.path.join(user_dir, f"*.{self.feature_format}"))

      if len(feature_files) < 3:
        issues.append(f"用户 {user_id} 的样本数量过少 ({len(feature_files)})")

      # 检查特征维度一致性
      shapes = []
      for file_path in feature_files:
        feature = np.load(file_path)
        shapes.append(feature.shape)

      if len(set(str(s) for s in shapes)) > 1:
        issues.append(f"用户 {user_id} 的特征维度不一致: {set(str(s) for s in shapes)}")

    return issues