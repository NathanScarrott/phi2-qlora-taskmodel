import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig

# Paths to your model and tokenizer
MODEL_DIR = "/Users/nathanscarrott/Documents/Finetune Phi-2/models/phi2-qlora"
BASE_MODEL = "microsoft/phi-2"

print("Loading tokenizer...")
# Load tokenizer from base model instead of adapter directory
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=False)
tokenizer.pad_token = tokenizer.eos_token

print("Loading base model...")
# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float32,  # Use float32 for CPU
    device_map="cpu",
    trust_remote_code=True
)

print("Loading LoRA adapter...")
# Check if adapter_model.safetensors exists, if not rename the final one
adapter_file = os.path.join(MODEL_DIR, "adapter_model.safetensors")
adapter_final_file = os.path.join(MODEL_DIR, "adapter_model_final.safetensors")

if not os.path.exists(adapter_file) and os.path.exists(adapter_final_file):
    print("Renaming adapter_model_final.safetensors to adapter_model.safetensors...")
    os.rename(adapter_final_file, adapter_file)

# Load LoRA adapter with local_files_only to avoid Hub validation
try:
    model = PeftModel.from_pretrained(
        base_model, 
        MODEL_DIR,
        local_files_only=True,
        is_trainable=False
    )
    model.eval()
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

def generate_response(user_input):
    prompt = f"""Convert the following user request into structured JSON format:

User: {user_input}

A:"""
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    
    print("  Generating response... (this may take a moment on CPU)")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=64,  # Reduced from 256 to speed up
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            # Removed temperature parameter
            repetition_penalty=1.1,  # Prevent repetition
            early_stopping=True,
            num_beams=1  # Greedy decoding for speed
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the new part (after the prompt)
    prompt_length = len(tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True))
    generated_text = response[prompt_length:].strip()
    
    # Fix: Stop at the first occurrence of repetition
    if '\nA:' in generated_text:
        generated_text = generated_text.split('\nA:')[0].strip()
    
    return generated_text

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing Fine-tuned Phi-2 LoRA Model")
    print("="*50)
    
    # Test all three intents your model was trained on
    test_inputs = [
        "remind me to call mom tomorrow at 3pm",
        "what's the weather like in New York?", 
        "send an email to John about the meeting at 2pm"
    ]
    
    for i, inp in enumerate(test_inputs, 1):
        print(f"\n[Test {i}]")
        print(f"User: {inp}")
        try:
            output = generate_response(inp)
            print(f"Model output: {output}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50) 