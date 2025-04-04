python:
voiceprint_project/
├── config/                      # 配置文件
│   └── config.yaml              # 全局配置参数
│
├── data/                        # 数据目录
│   ├── raw/                     # 原始音频
│   │   ├── user_1
│   │   ├── user_2
│   │   ├── user_3
│   │   └── ...                  # 不同用户的声音录制目录
│   │
│   └── processed/               # 处理后的特征
│
├── models/                      # 保存训练好的模型
│   └── README.md                # 模型说明
│ 
├── src/                         # 核心源代码
│   ├── audio/                   # 音频处理
│   │   ├── recorder.py          # 录音功能
│   │   └── processor.py         # 音频预处理
│   │
│   ├── features/                # 特征处理
│   │   └── extractor.py         # MFCC特征提取
│   │
│   ├── models/                  # 模型相关
│   │   ├── architecture.py      # 模型架构定义
│   │   ├── trainer.py           # 训练逻辑
│   │   └── converter.py         # TFLite转换
│   │
│   └── utils/                   # 工具函数
│       ├── visualization.py     # 可视化工具
│       └── evaluation.py        # 评估工具
│
├── scripts/                     # 可执行脚本
│   ├── collect_data.py          # 数据收集
│   ├── train.py                 # 训练模型
│   └── export_model.py          # 导出模型
│
└── .gitignore                   # git忽略文件

最终输出模型参数: 
(.venv) PS C:\GitHub\voiceprint_recognition\Python> python scripts/train.py
2025-04-03 20:46:51.337068: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2025-04-03 20:46:52.330163: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
初始化数据加载器...
检查数据完整性...
加载特征数据...
加载了 150 个特征样本，来自 5 个不同用户
划分数据集...
训练集: 105个样本, 验证集: 15个样本, 测试集: 30个样本
2025-04-03 20:46:54.457021: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: SSE3 SSE4.1 SSE4.2 AVX AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.        
WARNING:tensorflow:From C:\GitHub\voiceprint_recognition\Python\.venv\lib\site-packages\keras\src\backend\tensorflow\core.py:219: The name tf.placeholder is deprecated. Please use tf.compat.v1.placeholder instead.


开始训练模型...
准备训练数据...
验证集: 总样本对=30, 正例=15, 负例=15
验证集正负例比例: 0.50
开始训练模型...
Epoch 1/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 291ms/stepp - accuracy: 0.5459 - loss: 4.3915

验证集真实准确率: 0.5000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 8s 100ms/step - accuracy: 0.5445 - loss: 4.3792 - val_accuracy: 0.5000 - val_loss: 2.9597 - learning_rate: 0.0012
Epoch 2/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 74ms/stepep - accuracy: 0.5818 - loss: 2.9575

验证集真实准确率: 0.5000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 69ms/step - accuracy: 0.5787 - loss: 2.9460 - val_accuracy: 0.5000 - val_loss: 2.1448 - learning_rate: 0.0012
Epoch 3/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 61ms/stepep - accuracy: 0.6792 - loss: 2.1103

验证集真实准确率: 0.5000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 67ms/step - accuracy: 0.6776 - loss: 2.1024 - val_accuracy: 0.5000 - val_loss: 1.6319 - learning_rate: 0.0012
Epoch 4/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 66ms/stepep - accuracy: 0.7029 - loss: 1.5539

验证集真实准确率: 0.5000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 69ms/step - accuracy: 0.7026 - loss: 1.5516 - val_accuracy: 0.5000 - val_loss: 1.2634 - learning_rate: 0.0012
Epoch 5/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 65ms/stepep - accuracy: 0.7546 - loss: 1.2209

验证集真实准确率: 0.5000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 69ms/step - accuracy: 0.7534 - loss: 1.2166 - val_accuracy: 0.5000 - val_loss: 1.0000 - learning_rate: 0.0012
Epoch 6/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 58ms/stepep - accuracy: 0.7533 - loss: 0.9427

验证集真实准确率: 0.5000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 68ms/step - accuracy: 0.7527 - loss: 0.9421 - val_accuracy: 0.5000 - val_loss: 0.7956 - learning_rate: 0.0012
Epoch 7/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 66ms/stepep - accuracy: 0.8116 - loss: 0.7239

验证集真实准确率: 0.5000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 69ms/step - accuracy: 0.8108 - loss: 0.7220 - val_accuracy: 0.5000 - val_loss: 0.6224 - learning_rate: 0.0012
Epoch 8/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 73ms/stepep - accuracy: 0.8195 - loss: 0.5637

验证集真实准确率: 0.4667 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 72ms/step - accuracy: 0.8198 - loss: 0.5622 - val_accuracy: 0.4667 - val_loss: 0.4892 - learning_rate: 0.0012
Epoch 9/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 61ms/stepep - accuracy: 0.8052 - loss: 0.4633

验证集真实准确率: 0.4667 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 73ms/step - accuracy: 0.8047 - loss: 0.4626 - val_accuracy: 0.4667 - val_loss: 0.3867 - learning_rate: 0.0012
Epoch 10/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 67ms/stepep - accuracy: 0.8254 - loss: 0.3539

验证集真实准确率: 0.4000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 76ms/step - accuracy: 0.8259 - loss: 0.3536 - val_accuracy: 0.4000 - val_loss: 0.2997 - learning_rate: 0.0012
Epoch 11/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 75ms/stepep - accuracy: 0.8011 - loss: 0.2883

验证集真实准确率: 0.4000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 69ms/step - accuracy: 0.8010 - loss: 0.2881 - val_accuracy: 0.4000 - val_loss: 0.2572 - learning_rate: 0.0012
Epoch 12/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 60ms/stepep - accuracy: 0.8377 - loss: 0.2527 

验证集真实准确率: 0.4667 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 3s 111ms/step - accuracy: 0.8360 - loss: 0.2533 - val_accuracy: 0.4667 - val_loss: 0.4319 - learning_rate: 0.0012
Epoch 13/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 68ms/stepep - accuracy: 0.8316 - loss: 0.2094

验证集真实准确率: 0.3667 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 84ms/step - accuracy: 0.8300 - loss: 0.2099 - val_accuracy: 0.3667 - val_loss: 0.3479 - learning_rate: 0.0012
Epoch 14/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 68ms/stepep - accuracy: 0.7985 - loss: 0.1939

验证集真实准确率: 0.2667 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 84ms/step - accuracy: 0.7973 - loss: 0.1959 - val_accuracy: 0.2667 - val_loss: 0.1847 - learning_rate: 0.0012
Epoch 15/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 113ms/stepp - accuracy: 0.7713 - loss: 0.1930

验证集真实准确率: 0.3000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 3s 97ms/step - accuracy: 0.7713 - loss: 0.1931 - val_accuracy: 0.3000 - val_loss: 0.2068 - learning_rate: 0.0012
Epoch 16/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 73ms/stepep - accuracy: 0.8479 - loss: 0.1598 

验证集真实准确率: 0.4000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 90ms/step - accuracy: 0.8479 - loss: 0.1600 - val_accuracy: 0.4000 - val_loss: 0.1707 - learning_rate: 0.0012
Epoch 17/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 78ms/stepep - accuracy: 0.8684 - loss: 0.1264 

验证集真实准确率: 0.4000 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 3s 111ms/step - accuracy: 0.8652 - loss: 0.1268 - val_accuracy: 0.4000 - val_loss: 0.1568 - learning_rate: 0.0012
Epoch 18/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 62ms/steptep - accuracy: 0.8581 - loss: 0.1083

验证集真实准确率: 0.3333 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 3s 117ms/step - accuracy: 0.8560 - loss: 0.1083 - val_accuracy: 0.3333 - val_loss: 0.1391 - learning_rate: 0.0012
Epoch 19/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 66ms/stepep - accuracy: 0.8289 - loss: 0.0932

验证集真实准确率: 0.3667 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 77ms/step - accuracy: 0.8296 - loss: 0.0932 - val_accuracy: 0.3667 - val_loss: 0.0935 - learning_rate: 0.0012
Epoch 20/20
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 64ms/stepep - accuracy: 0.8628 - loss: 0.0753

验证集真实准确率: 0.2667 (阈值=0.30)
27/27 ━━━━━━━━━━━━━━━━━━━━ 2s 76ms/step - accuracy: 0.8628 - loss: 0.0752 - val_accuracy: 0.2667 - val_loss: 0.1017 - learning_rate: 0.0012

评估模型性能...
准备评估数据...
开始评估模型...
8/8 ━━━━━━━━━━━━━━━━━━━━ 0s 15ms/step - accuracy: 0.7521 - loss: 0.0924
测试集准确率: 0.7333, 损失: 0.0992
模型已保存至: models\voiceprint_model.keras
编码器已保存至: models\encoder_model.keras
模型已保存至: models\voiceprint_model.keras 和 models\encoder_model.keras
用户映射已保存至: models\user_mapping.npy
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 20934 (\N{CJK UNIFIED IDEOGRAPH-51C6}) missing from font(s) DejaVu Sans.
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 30830 (\N{CJK UNIFIED IDEOGRAPH-786E}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 29575 (\N{CJK UNIFIED IDEOGRAPH-7387}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 27169 (\N{CJK UNIFIED IDEOGRAPH-6A21}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 22411 (\N{CJK UNIFIED IDEOGRAPH-578B}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 21608 (\N{CJK UNIFIED IDEOGRAPH-5468}) missing from font(s) DejaVu Sans.
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 26399 (\N{CJK UNIFIED IDEOGRAPH-671F}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 35757 (\N{CJK UNIFIED IDEOGRAPH-8BAD}) missing from font(s) DejaVu Sans.
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 32451 (\N{CJK UNIFIED IDEOGRAPH-7EC3}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 39564 (\N{CJK UNIFIED IDEOGRAPH-9A8C}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 35777 (\N{CJK UNIFIED IDEOGRAPH-8BC1}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 25439 (\N{CJK UNIFIED IDEOGRAPH-635F}) missing from font(s) DejaVu Sans.
  plt.savefig(history_path)
C:\GitHub\voiceprint_recognition\Python\scripts\train.py:124: UserWarning: Glyph 22833 (\N{CJK UNIFIED IDEOGRAPH-5931}) missing from font(s) DejaVu Sans.  
  plt.savefig(history_path)
训练历史图表已保存至: logs\training_history.png

训练完成！
