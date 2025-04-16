idf_component_register(
    SRCS "voiceprint_lock.cpp" 
         "audio_processing.cpp" 
         "voiceprint_recognition.cpp" 
         "voiceprint_model.c"
    INCLUDE_DIRS "."

    REQUIRES esp-dsp esp_driver_i2s esp_driver_gpio esp-tflite-micro 
)
