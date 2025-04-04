import os
import argparse
import yaml
import sys
import numpy as np
import matplotlib.pyplot as plt

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.trainer import VoiceprintTrainer
from src.utils.data_loader import VoiceprintDataLoader

def main():
  parser = argparse.ArgumentParser(description='声纹识别模型训练工具')
  parser.add_argument('--config', type=str, default='config/config.yaml', help='配置文件路径')
  args = parser.parse_args()

  # 加载配置
  with open(args.config, 'r') as file:
    config = yaml.safe_load(file)

  # 确保输出目录存在
  output_dir = config['paths']['models_dir']
  os.makedirs(output_dir, exist_ok=True)

  # 创建日志目录
  logs_dir = config['paths']['logs_dir']
  os.makedirs(logs_dir, exist_ok=True)

  # 初始化数据加载器
  print("初始化数据加载器...")
  data_loader = VoiceprintDataLoader(config_path=args.config)

  # 检查数据完整性
  print("检查数据完整性...")
  issues = data_loader.check_data_integrity()
  if issues:
    print("发现以下数据问题：")
    for issue in issues:
      print(f"- {issue}")
    response = input("是否继续训练? (y/n): ")
    if response.lower() != 'y':
      print("训练已取消。")
      return

  # 加载特征数据
  print("加载特征数据...")
  features, labels, user_mapping = data_loader.load_features()

  if len(features) == 0:
    print("错误: 未找到特征数据。请先运行数据收集脚本。")
    return

  print(f"加载了 {len(features)} 个特征样本，来自 {len(np.unique(labels))} 个不同用户")

  # 检查每类样本数量
  user_counts = {user: sum(labels == i) for i, user in enumerate(user_mapping.values())}
  min_count = min(user_counts.values())
  if min_count < 3:
    print(f"警告: 某些用户样本数量过少(最少{min_count}个)，可能影响训练效果")

  # 数据划分
  print("划分数据集...")
  X_train, y_train, X_val, y_val, X_test, y_test = data_loader.split_dataset(features, labels)

  if X_val is not None:
    validation_data = (X_val, y_val)
    print(f"训练集: {X_train.shape[0]}个样本, 验证集: {X_val.shape[0]}个样本, 测试集: {X_test.shape[0]}个样本")
  else:
    validation_data = None
    print(f"训练集: {X_train.shape[0]}个样本, 测试集: {X_test.shape[0]}个样本")

  # 初始化训练器
  trainer = VoiceprintTrainer(config_path=args.config)

  # 训练模型
  print("\n开始训练模型...")
  history = trainer.train_model(X_train, y_train, validation_data)

  # 评估模型
  print("\n评估模型性能...")
  test_loss, test_accuracy = trainer.evaluate_model(X_test, y_test)
  print(f"测试集准确率: {test_accuracy:.4f}, 损失: {test_loss:.4f}")

  # 保存模型
  model_path = os.path.join(output_dir, 'voiceprint_model.keras')
  encoder_path = os.path.join(output_dir, 'encoder_model.keras')
  trainer.save_model(model_path, encoder_path)
  print(f"模型已保存至: {model_path} 和 {encoder_path}")

  # 保存用户ID映射
  mapping_path = os.path.join(output_dir, 'user_mapping.npy')
  np.save(mapping_path, user_mapping)
  print(f"用户映射已保存至: {mapping_path}")

  # 可视化训练历史
  if hasattr(history, 'history'):
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'])
    if 'val_accuracy' in history.history:
      plt.plot(history.history['val_accuracy'])
      plt.legend(['训练', '验证'], loc='lower right')
    else:
      plt.legend(['训练'], loc='lower right')
    plt.title('模型准确率')
    plt.ylabel('准确率')
    plt.xlabel('周期')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    if 'val_loss' in history.history:
      plt.plot(history.history['val_loss'])
      plt.legend(['训练', '验证'], loc='upper right')
    else:
      plt.legend(['训练'], loc='upper right')
    plt.title('模型损失')
    plt.ylabel('损失')
    plt.xlabel('周期')

    history_path = os.path.join(logs_dir, 'training_history.png')
    plt.savefig(history_path)
    print(f"训练历史图表已保存至: {history_path}")

  print("\n训练完成！")


if __name__ == "__main__":
  main()