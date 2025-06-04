FROM python:3.11-slim

# Install system dependencies including Git
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy deployment requirements
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the quantized model
COPY models/phi2-qlora-gguf/phi2-q4_k_m.gguf /app/models/phi2-qlora-gguf/

# Copy application code
COPY src/ .

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "inference/server.py"]