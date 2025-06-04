import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

MODEL_DIR = "/Users/nathanscarrott/Documents/Finetune Phi-2/models/phi2-qlora"
BASE_MODEL = "microsoft/phi-2"

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="cpu",
    trust_remote_code=True
)

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(
    base_model, 
    MODEL_DIR,
    local_files_only=True
)

print("Merging LoRA weights...")
merged_model = model.merge_and_unload()

print("Saving merged model...")
merged_model.save_pretrained("./models/phi2-merged")

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.save_pretrained("./models/phi2-merged")

print("Merged model saved to ./models/phi2-merged")
