#include "micro_interpreter.h"
#include "micro_mutable_op_resolver.h"
#include "schema_generated.h"
#include "all_ops_resolver.h"
#include "esp_log.h"
#include "voiceprint_model.h"
#include "audio_processing.h"

#define TAG "VOICEPRINT"
#define TENSOR_ARENA_SIZE (100 * 1024)

namespace {
  uint8_t tensor_arena[TENSOR_ARENA_SIZE];
  
  // 存储注册用户的声纹特征向量
  float registered_embeddings[5][128]; 
  int num_registered_users = 0;
  const int max_users = 5;
  
  // 相似度阈值，需要根据实际测试调整
  const float similarity_threshold = 0.85;
}

class VoiceprintRecognition {
public:
  bool Initialize() {
    // 加载模型
    model_ = tflite::GetModel(voiceprint_model);
    if (model_->version() != TFLITE_SCHEMA_VERSION) {
      ESP_LOGE(TAG, "模型版本不匹配!");
      return false;
    }

    // 解析模型中的所有操作
    static tflite::AllOpsResolver resolver;

    // 构建解释器
    static tflite::MicroInterpreter interpreter(
        model_, resolver, tensor_arena, TENSOR_ARENA_SIZE);
    interpreter_ = &interpreter;

    // 分配张量
    if (interpreter_->AllocateTensors() != kTfLiteOk) {
      ESP_LOGE(TAG, "AllocateTensors()失败!");
      return false;
    }

    // 获取输入输出张量
    input_ = interpreter_->input(0);
    output_ = interpreter_->output(0);
    
    ESP_LOGI(TAG, "声纹识别模型初始化完成");
    return true;
  }

  bool ExtractEmbedding(float* embedding) {
    int8_t feature_data[AUDIO_FEATURE_HEIGHT * AUDIO_FEATURE_WIDTH];
    
    if (!captureAndExtractFeatures(feature_data)) {
      return false;
    }
    
    // 将特征数据复制到模型输入张量
    int8_t* input_data = input_->data.int8;
    memcpy(input_data, feature_data, AUDIO_FEATURE_HEIGHT * AUDIO_FEATURE_WIDTH);
    
    // 运行推理
    if (interpreter_->Invoke() != kTfLiteOk) {
      ESP_LOGE(TAG, "推理失败!");
      return false;
    }
    
    // 获取输出并反量化
    int8_t* output_data = output_->data.int8;
    for (int i = 0; i < 128; i++) {
      // 反量化 (scale=0.0078125, zero_point=0)
      embedding[i] = output_data[i] * 0.0078125f;
    }
    
    // 归一化嵌入向量（L2范数）
    float sum_square = 0.0f;
    for (int i = 0; i < 128; i++) {
      sum_square += embedding[i] * embedding[i];
    }
    float norm = sqrt(sum_square);
    for (int i = 0; i < 128; i++) {
      embedding[i] /= norm;
    }
    
    return true;
  }
  
  bool RegisterUser(int user_id) {
    if (user_id >= max_users) {
      ESP_LOGE(TAG, "用户ID超出范围");
      return false;
    }
    
    float embedding[128];
    
    ESP_LOGI(TAG, "请说出注册口令...");
    if (!ExtractEmbedding(embedding)) {
      return false;
    }
    
    // 存储嵌入向量
    memcpy(registered_embeddings[user_id], embedding, sizeof(float) * 128);
    
    if (user_id >= num_registered_users) {
      num_registered_users = user_id + 1;
    }
    
    ESP_LOGI(TAG, "用户 %d 注册成功", user_id);
    return true;
  }
  
  int RecognizeUser() {
    float embedding[128];
    
    ESP_LOGI(TAG, "请说出识别口令...");
    if (!ExtractEmbedding(embedding)) {
      return -1;
    }
    
    // 寻找最匹配的用户
    float max_similarity = -1.0f;
    int best_match = -1;
    
    for (int i = 0; i < num_registered_users; i++) {
      float similarity = CalculateSimilarity(embedding, registered_embeddings[i]);
      
      ESP_LOGI(TAG, "与用户 %d 的相似度: %.4f", i, similarity);
      
      if (similarity > max_similarity) {
        max_similarity = similarity;
        best_match = i;
      }
    }
    
    // 检查是否达到阈值
    if (max_similarity >= similarity_threshold) {
      ESP_LOGI(TAG, "识别成功! 用户ID: %d, 相似度: %.4f", best_match, max_similarity);
      return best_match;
    } else {
      ESP_LOGI(TAG, "无法识别用户，最高相似度: %.4f", max_similarity);
      return -1;
    }
  }
  
private:
  // 计算余弦相似度
  float CalculateSimilarity(float* embedding1, float* embedding2) {
    float dot_product = 0.0f;
    
    for (int i = 0; i < 128; i++) {
      dot_product += embedding1[i] * embedding2[i];
    }
    
    // 因为向量已经归一化，所以点积就是余弦相似度
    return dot_product;
  }

  const tflite::Model* model_ = nullptr;
  tflite::MicroInterpreter* interpreter_ = nullptr;
  TfLiteTensor* input_ = nullptr;
  TfLiteTensor* output_ = nullptr;
};