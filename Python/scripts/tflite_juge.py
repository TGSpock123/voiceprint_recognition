import tensorflow as tf

def analyze_tflite_model(tflite_path):
    # Load TFLite model
    with open(tflite_path, 'rb') as f:
        tflite_model = f.read()

    # Load the interpreter
    interpreter = tf.lite.Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()

    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print("=== TFLite Model Analysis ===")
    print("Inputs:")
    for input_tensor in input_details:
        print(f" - Name: {input_tensor['name']}")
        print(f"   Shape: {input_tensor['shape']}")
        print(f"   Dtype: {input_tensor['dtype']}\n")

    print("Outputs:")
    for output_tensor in output_details:
        print(f" - Name: {output_tensor['name']}")
        print(f"   Shape: {output_tensor['shape']}")
        print(f"   Dtype: {output_tensor['dtype']}\n")

    # Check if INT8 quantization is used
    print("=== Quantization Details ===")
    for tensor in input_details + output_details:
        if 'quantization' in tensor:
            print(f" - Tensor: {tensor['name']}")
            print(f"   Quantization: {tensor['quantization']}")
        else:
            print(f" - Tensor: {tensor['name']} has no quantization info.")

# Example usage
analyze_tflite_model("C:\\GitHub\\voiceprint_recognition\\models\\voiceprint_model\\voiceprint_model.tflite")