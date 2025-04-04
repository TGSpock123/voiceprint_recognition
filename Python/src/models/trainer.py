import tensorflow as tf
import numpy as np
import os
import yaml
from .architecture import get_siamese_model
from datetime import datetime


class VoiceprintTrainer:
  def __init__(self, config_path='config/config.yaml'):
    # 设置全局随机种子确保可重现性
    tf.random.set_seed(42)
    np.random.seed(42)

    # 加载配置
    with open(config_path, 'r') as file:
      self.config = yaml.safe_load(file)

    # 获取模型
    self.siamese_model, self.encoder_model = get_siamese_model(config_path)

    # 配置训练参数
    self.learning_rate = self.config['model']['learning_rate'] * 3
    self.batch_size = self.config['model']['batch_size']
    self.epochs = self.config['model']['epochs']

    # 使用Contrastive Loss替代二元交叉熵
    self.margin = 1.0  # 对比损失的边界值

    # 编译模型使用对比损失
    self.siamese_model.compile(
      optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
      loss=self.contrastive_loss,
      metrics=['accuracy']
    )

  def contrastive_loss(self, y_true, y_pred):
    margin = 0.5  # 固定margin
    y_true = tf.cast(y_true, tf.float32)
    # 对于相似度度量: 同类相似度应大，异类相似度应小于margin
    return tf.reduce_mean(
        y_true * tf.square(1 - y_pred) +
        (1 - y_true) * tf.square(tf.maximum(0.0, y_pred - margin))
    )

  def prepare_pairs(self, features, labels, random_seed=None):
    """准备训练对"""
    # 如果提供了随机种子，设置随机状态
    if random_seed is not None:
      rng = np.random.RandomState(random_seed)
    else:
      rng = np.random.RandomState()

    num_samples = len(features)
    pairs = []
    pair_labels = []

    # 为每个样本生成一个正对(相同标签)和一个负对(不同标签)
    for i in range(num_samples):
      # 正对
      same_label_indices = np.where(labels == labels[i])[0]
      idx_positive = rng.choice(same_label_indices)
      pairs.append([features[i], features[idx_positive]])
      pair_labels.append(1)

      # 负对
      diff_label_indices = np.where(labels != labels[i])[0]
      idx_negative = rng.choice(diff_label_indices)
      pairs.append([features[i], features[idx_negative]])
      pair_labels.append(0)

    return np.array(pairs), np.array(pair_labels)

  def generate_batch(self, features, labels, batch_size):
    """生成训练批次"""
    while True:
      pairs, pair_labels = self.prepare_pairs(features, labels)
      indices = np.random.permutation(len(pairs))

      for start_idx in range(0, len(pairs), batch_size):
        end_idx = min(start_idx + batch_size, len(pairs))
        batch_indices = indices[start_idx:end_idx]

        batch_pairs = [pairs[batch_indices, 0], pairs[batch_indices, 1]]
        batch_labels = pair_labels[batch_indices]

        yield batch_pairs, batch_labels

  def train_model(self, features, labels, validation_data=None):
    """训练模型"""
    print("准备训练数据...")

    # 创建完整的训练对
    pairs, pair_labels = self.prepare_pairs(features, labels)

    # 构建完整的输入数据
    train_inputs = [pairs[:, 0], pairs[:, 1]]
    train_labels = pair_labels

    # 从配置获取路径
    models_dir = self.config['paths']['models_dir']
    logs_dir = self.config['paths']['logs_dir']

    # 确保目录存在
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    # 创建当前时间戳用于模型文件命名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    callbacks = [
      tf.keras.callbacks.ModelCheckpoint(
        filepath=os.path.join(models_dir, f'checkpoint_{timestamp}_{{epoch:02d}}_{{val_accuracy:.2f}}.keras'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max'
      ),
      tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=10,  # 增加耐心值，允许模型有更多时间收敛
        restore_best_weights=True
      ),
      tf.keras.callbacks.ReduceLROnPlateau(  # 添加学习率降低回调
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6
      ),
      tf.keras.callbacks.TensorBoard(
        log_dir=os.path.join(logs_dir, f'run_{timestamp}'),
        histogram_freq=1
      )
    ]

    val_inputs = None
    val_labels = None

    if validation_data is not None:
      val_features, val_labels_orig = validation_data
      # 生成验证样本对
      val_pairs, val_pair_labels = self.prepare_pairs(val_features, val_labels_orig, random_seed=42)
      val_inputs = [val_pairs[:, 0], val_pairs[:, 1]]
      val_labels = val_pair_labels

      # 打印验证数据统计
      print(
        f"验证集: 总样本对={len(val_labels)}, 正例={np.sum(val_labels)}, 负例={len(val_labels) - np.sum(val_labels)}")
      print(f"验证集正负例比例: {np.sum(val_labels) / len(val_labels):.2f}")

    print("开始训练模型...")
    history = self.siamese_model.fit(
      train_inputs,
      train_labels,
      batch_size=self.batch_size,
      epochs=self.epochs,
      validation_data=(val_inputs, val_labels) if validation_data is not None else None,
      callbacks=callbacks
    )

    return history

  def evaluate_model(self, features, labels):
    """评估模型性能"""
    print("准备评估数据...")

    # 使用固定种子生成测试样本对，确保结果可重现
    pairs, pair_labels = self.prepare_pairs(features, labels, random_seed=42)
    test_inputs = [pairs[:, 0], pairs[:, 1]]
    test_labels = pair_labels

    print("开始评估模型...")
    metrics = self.siamese_model.evaluate(
      test_inputs,
      test_labels,
      batch_size=self.batch_size
    )

    # 返回损失和准确率
    return metrics[0], metrics[1]

  def save_model(self, model_path=None, encoder_path=None):
    """保存模型"""
    # 如果未提供路径，使用配置中的默认路径
    if model_path is None:
      model_path = os.path.join(self.config['paths']['models_dir'], 'voiceprint_model.keras')

    if encoder_path is None:
      encoder_path = os.path.join(self.config['paths']['models_dir'], 'encoder_model.keras')

    # 确保目录存在
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(encoder_path), exist_ok=True)

    self.siamese_model.save(model_path)
    self.encoder_model.save(encoder_path)
    print(f"模型已保存至: {model_path}")
    print(f"编码器已保存至: {encoder_path}")

    return model_path, encoder_path