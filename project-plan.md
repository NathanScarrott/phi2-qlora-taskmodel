PHI-2 QLORA MODEL PROJECT PLAN

Environment:
- GitHub repository: `https://github.com/NathanScarrott/phi2-qlora-taskmodel`
- Hardware: `2021 MacBook Pro M1 Pro, 16 GB RAM`
- External LLM for data generation: **Gemini 2.5 / Gemini Flash 2.0** (via **OpenRouter**)

---
## Repository Structure
```
project-root/
├── README.md                # Project overview and quick‑start
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignore rules
├── .env.example             # Example env variables
│
├── data/                    # Raw → processed datasets
├── notebooks/               # Colab fine‑tuning notebook
├── src/                     # Code (dataset script, training driver, FastAPI server, utils)
├── models/                  # Checkpoints + quantised GGUF
└── tests/                   # PyTest suite
```

---
## Phase 1 – Setup Environment
1. Add dependencies to `requirements.txt` (transformers, peft, datasets, bitsandbytes, trl, fastapi, uvicorn, llama‑cpp‑python, requests, python‑dotenv).
2. `pip install -r requirements.txt`.
3. Verify PyTorch MPS support (`torch.backends.mps.is_available()`).
4. Populate `.env` with your `OPENROUTER_API_KEY` and default `GEN_MODEL` (e.g. `google/gemini-pro-2.5`).

---
## Phase 2 – Dataset Preparation
1. **Define the task**: convert informal task requests containing time expressions into a concise `<task> <when>` form.
2. **Generate examples with an LLM**:
   - Write a small script (`src/data/generate_dataset.py`) that calls the OpenRouter API.
   - Use a single prompt instructing Gemini to return a JSON object with `input` and `output` keys.
   - Loop until you have ~1 000 diverse examples; write each as a line in `data/task_dataset.jsonl`.
3. **Split** dataset into `train.jsonl` (80 %) and `val.jsonl` (20 %) under `data/processed/`.

---
## Phase 3 – Fine‑Tuning Phi‑2 with QLoRA (Google Colab)
1. Open `notebooks/fine_tuning_colab.ipynb`.
2. Mount Drive or pull the dataset from GitHub.
3. Configure PEFT LoRA (rank 8, alpha 16 is a sensible default).
4. Train for ~3 epochs, monitoring validation loss.
5. Save the Hugging Face checkpoint to `models/phi2-qlora/`.

---
## Phase 4 – Quantise to GGUF (Q4_K_M)
1. Run llama.cpp `convert.py` (or equivalent) on the Colab instance.
2. Download the resulting `.gguf` files to `models/phi2-qlora-gguf/` on your Mac.
3. Test local inference with `llama‑cpp‑python` to confirm it loads.

---
## Phase 5 – Inference API (FastAPI)
1. **Local Development**:
   - Create `src/inference/server.py` that:
     - Loads the GGUF model via `llama‑cpp‑python`.
     - Exposes a `/convert` POST endpoint receiving JSON `{"text": "<input>"}`.
     - Returns the model's concise rewrite.
   - Test locally with `uvicorn src.inference.server:app --reload`.

2. **EC2 Deployment**:
   - Launch an EC2 instance (t3.medium or c5.large recommended)
   - Install dependencies: Python, pip, your requirements
   - Copy your model files (`models/phi2-qlora-gguf/`) to the instance
   - Configure security group to allow HTTP/HTTPS traffic
   - Run server with: `uvicorn src.inference.server:app --host 0.0.0.0 --port 8000`
   - Optional: Set up systemd service for auto-restart
   - Optional: Add nginx reverse proxy with SSL certificate

3. **Environment Configuration**:
   - Update `.env` to include `API_BASE_URL=http://your-ec2-instance:8000`
   - Test API endpoint: `curl -X POST http://your-ec2-instance:8000/predict -H "Content-Type: application/json" -d '{"text": "remind me to call mom tomorrow"}'`
---
## Phase 6 – Voice‑Assistant Integration
1. From your assistant code, POST the user’s transcribed text to `/predict`.
2. Parse the response and execute the corresponding task logic (calendar entry, reminder, etc.).

---
## Phase 7 – Testing & CI
- Add unit tests for dataset integrity and API responses in `tests/`.
- Optional: GitHub Actions workflow to run `pytest` on push.

---
## Phase 8 – Documentation & Cleanup
- Update `README.md` with setup steps, environment variables, and model‑switch instructions for OpenRouter.
- Commit, push, and tag a release once pipeline is stable.

### Key External Resources
- OpenRouter API docs
- Gemini 2.5 / Flash 2.0 model cards
- Hugging Face PEFT & QLoRA tutorial
- llama.cpp GGUF guide
- FastAPI documentation