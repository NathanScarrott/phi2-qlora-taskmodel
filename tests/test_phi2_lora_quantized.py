# test_gguf_model.py
from llama_cpp import Llama
import time

print("Loading GGUF model...")
start_time = time.time()

llm = Llama(
    model_path="./models/phi2-qlora-gguf/phi2-q4_k_m.gguf",
    n_ctx=2048,
    n_threads=8,  # Use multiple cores on M1 Pro
    verbose=False
)

load_time = time.time() - start_time
print(f"Model loaded in {load_time:.2f} seconds")

def test_gguf_model(user_input):
    prompt = f"""Convert the following user request into structured JSON format:

User: {user_input}

Assistant:"""
    
    start_time = time.time()
    output = llm(
        prompt,
        max_tokens=100,
        temperature=0.1,
        stop=["\n\nUser:", "\nA:", "Follow-up"],
        echo=False
    )
    inference_time = time.time() - start_time
    
    response = output['choices'][0]['text'].strip()
    return response, inference_time

# Test cases
test_inputs = [
    "remind me to call mom tomorrow at 3pm",
    "what's the weather like in New York?", 
    "send an email to John about the meeting"
]

print("\n" + "="*60)
print("Testing Quantized GGUF Model (Q4_K_M)")
print("="*60)

for i, inp in enumerate(test_inputs, 1):
    print(f"\n[Test {i}]")
    print(f"User: {inp}")
    result, inference_time = test_gguf_model(inp)
    print(f"Model: {result}")
    print(f"⚡ Inference time: {inference_time:.2f} seconds")
    print("-" * 40)