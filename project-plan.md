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
## Phase 5 – Production Deployment (AWS Kubernetes)

1. **Local Development**:
   - Create `src/inference/server.py` that:
     - Loads the GGUF model via `llama-cpp-python`
     - Exposes `/health` GET endpoint for health checks
     - Exposes `/api/convert` POST endpoint receiving JSON `{"text": "<input>"}`
     - Returns structured JSON with intent classification and extracted entities
   - Test locally with `uvicorn src.inference.server:app --reload`

2. **Docker Containerization**:
   - Create `Dockerfile` with Python 3.11-slim base image
   - Install system dependencies: `build-essential`, `git`, `cmake`
   - Create optimized `requirements-docker.txt` with minimal dependencies:
     - `fastapi==0.104.1`
     - `uvicorn[standard]==0.24.0` 
     - `llama-cpp-python==0.2.85` (Phi-2 architecture support)
     - `pydantic==2.5.0`
   - Copy quantized model and source code into container
   - Build multi-platform image: `docker build --platform linux/amd64`

3. **AWS Infrastructure Setup**:
   - Create AWS account with billing alerts and budget controls
   - Set up IAM user with programmatic access and EKS permissions
   - Configure AWS CLI with `eu-west-2` region
   - Create ECR repository for Docker image storage
   - Push Docker image to ECR: `045306124706.dkr.ecr.eu-west-2.amazonaws.com/phi2-fastapi`

4. **Kubernetes Deployment (EKS)**:
   - Create EKS cluster configuration (`eks-cluster.yaml`):
     - Instance type: `m6g.large` (ARM64 Graviton3 for optimal performance)
     - Spot instances for cost optimization
     - Auto-scaling: 1-3 nodes
   - Deploy cluster: `eksctl create cluster -f eks-cluster.yaml` (~20 minutes)
   - Create Kubernetes deployment configuration (`k8s/deployment.yaml`):
     - Resource limits: 3GB memory, 2 CPU cores
     - Health checks on `/health` endpoint  
     - LoadBalancer service for external access
   - Deploy application: `kubectl apply -f k8s/deployment.yaml`

5. **Production Testing & Monitoring**:
   - Verify health endpoint: `GET /health` returns `{"status": "healthy", "model": "phi2-qlora-q4_k_m"}`
   - Test API endpoint with various intents:
     ```bash
     curl -X POST "http://load-balancer-url/api/convert" \
       -H "Content-Type: application/json" \
       -d '{"text": "Add buy groceries to my todo list"}'
     ```
   - Monitor performance: ~20-25 seconds per inference on ARM64 (3x faster than x86_64)
   - Monitor costs and scale down when not in use: `eksctl scale nodegroup --nodes=0`

6. **Cost Management**:
   - **Development**: Scale to 0 nodes overnight (saves ~£0.30/day)
   - **Production**: ~£1/day for 24/7 availability
   - **Cleanup**: `eksctl delete cluster` when experimenting complete
   - **Performance vs Cost**: ARM64 m6g.large provides best price/performance ratio

7. **Performance Characteristics**:
   - **Model loading**: ~21 seconds (one-time startup cost)
   - **Inference time**: 20-25 seconds per request (CPU-only ARM64)
   - **Memory usage**: ~2GB (model + FastAPI overhead)
   - **Throughput**: 1 concurrent request (single replica)
   - **Scaling**: Can increase replicas for higher throughput

8. **Production URL & Usage**:
   - **Live endpoint**: AWS Load Balancer provides public URL
   - **Health monitoring**: Kubernetes automatically restarts failed containers
   - **API format**: Returns structured JSON with intent classification:
     ```json
     {
       "success": true,
       "structured_data": {
         "intent": "add_task",
         "task": "buy groceries"
       }
     }
     ```
---
## Phase 6 – Voice‑Assistant Integration
1. From your assistant code, POST the user’s transcribed text to `/convert`.
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