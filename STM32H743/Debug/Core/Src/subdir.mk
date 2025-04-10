################################################################################
# 自动生成的文件。不要编辑！
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# 将这些工具调用的输入和输出添加到构建变量 
C_SRCS += \
../Core/Src/audio_processing.c \
../Core/Src/dma.c \
../Core/Src/feature_extraction.c \
../Core/Src/freertos.c \
../Core/Src/gpio.c \
../Core/Src/i2s.c \
../Core/Src/main.c \
../Core/Src/memorymap.c \
../Core/Src/rtc.c \
../Core/Src/stm32h7xx_hal_msp.c \
../Core/Src/stm32h7xx_hal_timebase_tim.c \
../Core/Src/stm32h7xx_it.c \
../Core/Src/sysmem.c \
../Core/Src/system_stm32h7xx.c \
../Core/Src/usart.c \
../Core/Src/user_interface.c \
../Core/Src/voice_recognition.c 

OBJS += \
./Core/Src/audio_processing.o \
./Core/Src/dma.o \
./Core/Src/feature_extraction.o \
./Core/Src/freertos.o \
./Core/Src/gpio.o \
./Core/Src/i2s.o \
./Core/Src/main.o \
./Core/Src/memorymap.o \
./Core/Src/rtc.o \
./Core/Src/stm32h7xx_hal_msp.o \
./Core/Src/stm32h7xx_hal_timebase_tim.o \
./Core/Src/stm32h7xx_it.o \
./Core/Src/sysmem.o \
./Core/Src/system_stm32h7xx.o \
./Core/Src/usart.o \
./Core/Src/user_interface.o \
./Core/Src/voice_recognition.o 

C_DEPS += \
./Core/Src/audio_processing.d \
./Core/Src/dma.d \
./Core/Src/feature_extraction.d \
./Core/Src/freertos.d \
./Core/Src/gpio.d \
./Core/Src/i2s.d \
./Core/Src/main.d \
./Core/Src/memorymap.d \
./Core/Src/rtc.d \
./Core/Src/stm32h7xx_hal_msp.d \
./Core/Src/stm32h7xx_hal_timebase_tim.d \
./Core/Src/stm32h7xx_it.d \
./Core/Src/sysmem.d \
./Core/Src/system_stm32h7xx.d \
./Core/Src/usart.d \
./Core/Src/user_interface.d \
./Core/Src/voice_recognition.d 


# 每个子目录必须为构建它所贡献的源提供规则
Core/Src/%.o Core/Src/%.su Core/Src/%.cyclo: ../Core/Src/%.c Core/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m7 -std=gnu11 -g3 -DDEBUG -DUSE_PWR_LDO_SUPPLY -DUSE_HAL_DRIVER -DSTM32H743xx -DARM_MATH_CM7 -D__TARGET_FPU_VFP -c -I../Core/Inc -I../Drivers/STM32H7xx_HAL_Driver/Inc -I../Drivers/STM32H7xx_HAL_Driver/Inc/Legacy -I../Middlewares/Third_Party/FreeRTOS/Source/include -I../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2 -I../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F -I../Drivers/CMSIS/Device/ST/STM32H7xx/Include -I../Drivers/CMSIS/Include -I"C:/GitHub/voiceprint_recognition/STM32H743/Middlewares/Third_Party/RTT" -I"C:/GitHub/voiceprint_recognition/STM32H743/Middlewares/Third_Party/EasyLogger/inc" -I../X-CUBE-AI/App -I../X-CUBE-AI -I../X-CUBE-AI/Target -I../Middlewares/ST/AI/Inc -I"C:/GitHub/voiceprint_recognition/STM32H743/Middlewares/ST/ARM/DSP/Inc" -I../Middlewares/ST/ARM/DSP/Inc -Os -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv5-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Core-2f-Src

clean-Core-2f-Src:
	-$(RM) ./Core/Src/audio_processing.cyclo ./Core/Src/audio_processing.d ./Core/Src/audio_processing.o ./Core/Src/audio_processing.su ./Core/Src/dma.cyclo ./Core/Src/dma.d ./Core/Src/dma.o ./Core/Src/dma.su ./Core/Src/feature_extraction.cyclo ./Core/Src/feature_extraction.d ./Core/Src/feature_extraction.o ./Core/Src/feature_extraction.su ./Core/Src/freertos.cyclo ./Core/Src/freertos.d ./Core/Src/freertos.o ./Core/Src/freertos.su ./Core/Src/gpio.cyclo ./Core/Src/gpio.d ./Core/Src/gpio.o ./Core/Src/gpio.su ./Core/Src/i2s.cyclo ./Core/Src/i2s.d ./Core/Src/i2s.o ./Core/Src/i2s.su ./Core/Src/main.cyclo ./Core/Src/main.d ./Core/Src/main.o ./Core/Src/main.su ./Core/Src/memorymap.cyclo ./Core/Src/memorymap.d ./Core/Src/memorymap.o ./Core/Src/memorymap.su ./Core/Src/rtc.cyclo ./Core/Src/rtc.d ./Core/Src/rtc.o ./Core/Src/rtc.su ./Core/Src/stm32h7xx_hal_msp.cyclo ./Core/Src/stm32h7xx_hal_msp.d ./Core/Src/stm32h7xx_hal_msp.o ./Core/Src/stm32h7xx_hal_msp.su ./Core/Src/stm32h7xx_hal_timebase_tim.cyclo ./Core/Src/stm32h7xx_hal_timebase_tim.d ./Core/Src/stm32h7xx_hal_timebase_tim.o ./Core/Src/stm32h7xx_hal_timebase_tim.su ./Core/Src/stm32h7xx_it.cyclo ./Core/Src/stm32h7xx_it.d ./Core/Src/stm32h7xx_it.o ./Core/Src/stm32h7xx_it.su ./Core/Src/sysmem.cyclo ./Core/Src/sysmem.d ./Core/Src/sysmem.o ./Core/Src/sysmem.su ./Core/Src/system_stm32h7xx.cyclo ./Core/Src/system_stm32h7xx.d ./Core/Src/system_stm32h7xx.o ./Core/Src/system_stm32h7xx.su ./Core/Src/usart.cyclo ./Core/Src/usart.d ./Core/Src/usart.o ./Core/Src/usart.su ./Core/Src/user_interface.cyclo ./Core/Src/user_interface.d ./Core/Src/user_interface.o ./Core/Src/user_interface.su ./Core/Src/voice_recognition.cyclo ./Core/Src/voice_recognition.d ./Core/Src/voice_recognition.o ./Core/Src/voice_recognition.su

.PHONY: clean-Core-2f-Src

