# The Secret Weapon: Local Quantized LLM Deployment Guide

This guide details the deployment of a local, 4-bit quantized Large Language Model (LLM) to power Solomon's cognitive planning and reasoning engine without relying on external cloud credits or internet dependencies.

---

## 1. What is Quantization? (The Secret Weapon)

When running large language models on local hardware, memory footprint is the primary bottleneck. Standard models utilize 16-bit floating-point weights (FP16), meaning a 7-billion parameter model requires around **14 GB of system memory** just to load, plus additional memory for the context window.

**Quantization** is a optimization technique that compresses the model by reducing the precision of its weights (e.g., from 16-bit to 4-bit integers).
- A **7B or 8B parameter model** compressed to **4-bit precision (using the GGUF format)** will require only **4 to 5 GB of system RAM/VRAM**.
- This compression retains over 95%+ of the model's original capabilities while allowing it to run at lightning-fast speeds on old, entry-level, or consumer-grade hardware.

---

## 2. Deploying Local Quantized Models

We support two primary local LLM servers that expose OpenAI-compatible APIs out of the box: **Ollama** and **llama.cpp**.

### Option A: Setup using Ollama (Recommended)

Ollama is the simplest tool for running local models. It manages downloads, quantization layers, and hardware acceleration automatically.

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull the Quantized 4-bit Model:**
   To pull a highly performant 4-bit quantized model (e.g., Llama 3 or Mistral):
   ```bash
   ollama pull llama3:8b-instruct-q4_K_M
   ```

3. **Verify the OpenAI-Compatible API is Active:**
   Ollama automatically runs a background service on port `11434`. You can query its OpenAI-compatible endpoint:
   ```bash
   curl http://localhost:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "llama3:8b-instruct-q4_K_M",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

---

### Option B: Setup using llama.cpp

For advanced tuning, maximum portability, and zero-dependency compilation:

1. **Clone and Build llama.cpp:**
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make -j
   ```

2. **Download a 4-bit GGUF Model:**
   Download a model from HuggingFace (e.g., Meta-Llama-3-8B-Instruct-Q4_K_M.gguf) into your directory.

3. **Start the OpenAI-Compatible Server:**
   Run the embedded server on port `8080`:
   ```bash
   ./llama-server -m models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf -c 4096 --port 8080
   ```

---

## 3. Connecting Solomon to your Local Quantized LLM

To configure the Solomon API gateway (`app.py` / `solomon_api_server.py`) to leverage your local quantized server instead of the public OpenAI API cloud, configure the following environment variables:

```bash
# 1. Point the API Base URL to your local server's OpenAI translation layer
export SOLOMON_LLM_API_BASE="http://127.0.0.1:11434/v1" # Or http://127.0.0.1:8080/v1 for llama.cpp

# 2. Specify the exact model identifier pulled/run locally
export SOLOMON_MODEL="llama3:8b-instruct-q4_K_M"

# 3. Optional: A placeholder local API key if needed (the app will default to 'local_quantized_key')
export OPENAI_API_KEY="local_quantized_key"
```

### Verification
When Solomon boots, the log will output:
```text
[INFO] Local quantized LLM API configured with base URL: http://127.0.0.1:11434/v1
```
All chat, planning, and reasoning queries routed through `/api/command-center/solomon-chat` will now execute entirely in your local, resource-capped sandbox!
