from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from llama_cpp import Llama
import json
import re
import os
from pydantic import BaseModel

app = FastAPI()

# Debug: Print current directory and files
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current dir: {os.listdir('.')}")
if os.path.exists("models"):
    print(f"Files in models/: {os.listdir('models')}")
    if os.path.exists("models/phi2-qlora-gguf"):
        print(f"Files in models/phi2-qlora-gguf/: {os.listdir('models/phi2-qlora-gguf')}")

model_path = "./models/phi2-qlora-gguf/phi2-q4_k_m.gguf"
print(f"Trying to load model from: {model_path}")
print(f"Model file exists: {os.path.exists(model_path)}")

# Load your actual quantized model
llm = Llama(
    model_path=model_path,
    n_ctx=512,
    n_threads=8,
    verbose=True  # More debug output
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    text: str

def extract_json(text):
    """Extract the first complete JSON object from model output"""
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
    if json_match:
        json_str = json_match.group()
        try:
            # Validate it's proper JSON
            parsed = json.loads(json_str)
            return parsed
        except:
            return {"error": "Invalid JSON generated", "raw_output": json_str}
    return {"error": "No JSON found", "raw_output": text}

@app.post("/api/convert")
async def convert_request(data: UserRequest):
    """Convert natural language request to structured JSON format"""
    
    # Use your model's exact training format
    prompt = f"""Convert the following user request into structured JSON format:

User: {data.text}

Assistant:"""
    
    try:
        output = llm(
            prompt,
            max_tokens=100,
            temperature=0.1,
            stop=["\n\nUser:", "\nA:", "Follow-up"],
            echo=False
        )
        
        # Extract the response text
        response_text = output["choices"][0]["text"].strip()
        
        # Extract and validate JSON
        structured_data = extract_json(response_text)
        
        return {
            "success": True,
            "structured_data": structured_data,
            "raw_output": response_text
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "structured_data": None
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": "phi2-qlora-q4_k_m"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)