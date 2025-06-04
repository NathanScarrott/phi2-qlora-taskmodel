# PHI-2 QLORA Task Model

A fine-tuned version of Microsoft's PHI-2 model that converts informal task requests containing time expressions into a concise `<task> <when>` format.

## Overview

This project fine-tunes the PHI-2 model using QLoRA (Quantized Low-Rank Adaptation) to efficiently create a specialized task formatting model with minimal computational resources.

## Project Structure

```
project-root/
├── README.md                # Project overview and quick-start
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignore rules
├── .env.example             # Example env variables
│
├── data/                    # Raw → processed datasets
├── notebooks/               # Colab fine-tuning notebook
├── src/                     # Code (dataset script, training driver, FastAPI server, utils)
├── models/                  # Checkpoints + quantised GGUF
└── tests/                   # PyTest suite
```

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your OpenRouter API key
4. Follow steps in the project phases to generate data, fine-tune, and deploy

## Environment

- Hardware: 2021 MacBook Pro M1 Pro, 16 GB RAM
- External LLM for data generation: Gemini 2.5 / Gemini Flash 2.0 (via OpenRouter)

## License

[MIT License](LICENSE)
