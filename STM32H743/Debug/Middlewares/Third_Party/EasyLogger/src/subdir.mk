################################################################################
# 自动生成的文件。不要编辑！
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# 将这些工具调用的输入和输出添加到构建变量 
C_SRCS += \
../Middlewares/Third_Party/EasyLogger/src/elog.c \
../Middlewares/Third_Party/EasyLogger/src/elog_utils.c 

OBJS += \
./Middlewares/Third_Party/EasyLogger/src/elog.o \
./Middlewares/Third_Party/EasyLogger/src/elog_utils.o 

C_DEPS += \
./Middlewares/Third_Party/EasyLogger/src/elog.d \
./Middlewares/Third_Party/EasyLogger/src/elog_utils.d 


# 每个子目录必须为构建它所贡献的源提供规则
Middlewares/Third_Party/EasyLogger/src/%.o Middlewares/Third_Party/EasyLogger/src/%.su Middlewares/Third_Party/EasyLogger/src/%.cyclo: ../Middlewares/Third_Party/EasyLogger/src/%.c Middlewares/Third_Party/EasyLogger/src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m7 -std=gnu11 -g3 -DDEBUG -DUSE_PWR_LDO_SUPPLY -DUSE_HAL_DRIVER -DSTM32H743xx -DARM_MATH_CM7 -D__TARGET_FPU_VFP -c -I../Core/Inc -I../Drivers/STM32H7xx_HAL_Driver/Inc -I../Drivers/STM32H7xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32H7xx/Include -I../Drivers/CMSIS/Include -I"C:/GitHub/voiceprint_recognition/STM32H743/Middlewares/Third_Party/RTT" -I"C:/GitHub/voiceprint_recognition/STM32H743/Middlewares/Third_Party/EasyLogger/inc" -I../X-CUBE-AI/App -I../X-CUBE-AI -I../Middlewares/ST/AI/Inc -I"C:/GitHub/voiceprint_recognition/STM32H743/Middlewares/ST/ARM/DSP/Inc" -I../Middlewares/ST/ARM/DSP/Inc -I../X-CUBE-AI/Target -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv5-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Middlewares-2f-Third_Party-2f-EasyLogger-2f-src

clean-Middlewares-2f-Third_Party-2f-EasyLogger-2f-src:
	-$(RM) ./Middlewares/Third_Party/EasyLogger/src/elog.cyclo ./Middlewares/Third_Party/EasyLogger/src/elog.d ./Middlewares/Third_Party/EasyLogger/src/elog.o ./Middlewares/Third_Party/EasyLogger/src/elog.su ./Middlewares/Third_Party/EasyLogger/src/elog_utils.cyclo ./Middlewares/Third_Party/EasyLogger/src/elog_utils.d ./Middlewares/Third_Party/EasyLogger/src/elog_utils.o ./Middlewares/Third_Party/EasyLogger/src/elog_utils.su

.PHONY: clean-Middlewares-2f-Third_Party-2f-EasyLogger-2f-src

