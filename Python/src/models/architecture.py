import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Dense, Flatten, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
import yaml


def get_siamese_model(config_path='config/config.yaml'):
  """创建孪生网络模型"""
  # 加载配置
  with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

  input_shape = config['model']['input_shape'][1:]  # 去掉batch_size维度
  input_shape = tuple(None if dim == 'None' else dim for dim in input_shape)
  embedding_dim = config['model']['embedding_dim']

  # 添加L2正则化系数
  reg_factor = 0.01

  def build_encoder():
    inp = Input(shape=input_shape)

    # 第一个卷积块
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(inp)
    x = BatchNormalization()(x)
    x = MaxPooling2D((2, 2))(x)
    x = Dropout(0.1)(x)

    # 第二个卷积块
    x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D((2, 2))(x)
    x = Dropout(0.2)(x)

    # 第三个卷积块
    x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)

    # 添加通道注意力 (Squeeze-and-Excitation) - 添加了L2正则化
    se = tf.keras.layers.GlobalAveragePooling2D()(x)
    se = Dense(128 // 16, activation='relu', kernel_regularizer=l2(reg_factor))(se)  # 添加L2正则化
    se = Dense(128, activation='sigmoid', kernel_regularizer=l2(reg_factor))(se)  # 添加L2正则化
    se = tf.keras.layers.Reshape((1, 1, 128))(se)
    x = tf.keras.layers.multiply([x, se])

    # 添加空间注意力
    avg_pool = tf.keras.layers.Lambda(lambda x: tf.reduce_mean(x, axis=-1, keepdims=True))(x)
    max_pool = tf.keras.layers.Lambda(lambda x: tf.reduce_max(x, axis=-1, keepdims=True))(x)
    concat = tf.keras.layers.Concatenate()([avg_pool, max_pool])
    spatial = Conv2D(1, (7, 7), padding='same', activation='sigmoid')(concat)
    x = tf.keras.layers.multiply([x, spatial])

    x = MaxPooling2D((2, 2))(x)
    x = Dropout(0.3)(x)

    # 全局池化替代展平层
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu', kernel_regularizer=l2(reg_factor))(x)  # 添加L2正则化
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)

    # 嵌入层 - 添加了L2正则化
    x = Dense(embedding_dim, activation=None, kernel_regularizer=l2(reg_factor))(x)  # 添加L2正则化

    # L2正则化以便在特征空间中计算距离
    embeddings = tf.keras.layers.Lambda(lambda x: tf.nn.l2_normalize(x, axis=1))(x)

    return Model(inputs=inp, outputs=embeddings)

  # 构建编码器
  encoder = build_encoder()

  # 构建孪生网络
  input_a = Input(shape=input_shape)
  input_b = Input(shape=input_shape)

  embedding_a = encoder(input_a)
  embedding_b = encoder(input_b)

  # 创建只有编码器的模型（用于推理）
  encoder_model = Model(inputs=input_a, outputs=embedding_a)

  # 创建用于训练的模型
  merged_vector = tf.keras.layers.Lambda(
    lambda x: tf.reduce_sum(x[0] * x[1], axis=1, keepdims=True) /
              (tf.sqrt(tf.reduce_sum(tf.square(x[0]), axis=1, keepdims=True)) *
               tf.sqrt(tf.reduce_sum(tf.square(x[1]), axis=1, keepdims=True)))
  )([embedding_a, embedding_b])
  output = merged_vector  # 直接输出相似度，不使用sigmoid

  siamese_model = Model(inputs=[input_a, input_b], outputs=output)

  return siamese_model, encoder_model