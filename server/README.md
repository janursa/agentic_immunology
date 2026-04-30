# Gemma Server — Setup & Usage

## Overview

Two things run simultaneously to serve the model:

```
Your laptop / collaborator
        │
        │  HTTPS  https://xxxx.ngrok.io/v1
        ▼
   ngrok cloud  ← relay, no compute here
        │
        │  forwards to
        ▼
   login node   ← start_ngrok.sh runs here
        │
        │  cluster-internal  bioinf034:8080
        ▼
   bioinf034    ← llama-server + 26B model (SLURM job)
```

**ngrok** is just a tunnel/proxy — it does not run the model.  
**llama-server** runs the model on the GPU node and is only reachable inside the cluster.  
ngrok bridges the two, giving the model a public HTTPS URL.

---

## First-time setup

### 1. Get a free ngrok auth token
Sign up at https://dashboard.ngrok.com → copy your token → paste into `.env`:
```
NGROK_AUTHTOKEN=your_token_here
```
Without this the tunnel expires after 2 hours. With it, it stays up indefinitely.

### 2. The `.env` file
Located at `agentic_immunology/.env`. Contains:
```
GEMMA_URL=https://xxxx.ngrok.io/v1    # updated automatically by start_ngrok.sh
GEMMA_API_KEY=sk-...                   # secret — share only with trusted users
NGROK_AUTHTOKEN=...                    # your ngrok token
```
**Keep this file private — it contains secrets.**

---

## Running the server

### Step 1 — Start the model (SLURM job, compute node)
```bash
cd agentic_immunology/server
sbatch server_gemma4.sh
```
- Runs on **bioinf034** (A100 GPU)
- Model: `gemma-4-26B-A4B UD-Q5_K_M` (~21 GB)
- Job time limit: 24 hours — resubmit when it expires
- Check status: `squeue -u $USER --name=gemma4-server`

### Step 2 — Start the tunnel (login node, keep terminal open)
```bash
bash agentic_immunology/server/start_ngrok.sh
```
- Waits for the model to be reachable, then opens the tunnel
- Prints the public URL
- **Automatically updates `GEMMA_URL` in `.env`**
- Keep this terminal open — closing it kills the tunnel

---

## Using the API

Once both are running, anyone with the URL and API key can call the model.

### Python (openai library)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://xxxx.ngrok.io/v1",   # from .env GEMMA_URL
    api_key="sk-...",                        # from .env GEMMA_API_KEY
)

response = client.chat.completions.create(
    model="gemma",
    messages=[{"role": "user", "content": "Compare CD4T and CD8T aging signatures"}],
    max_tokens=2048,
)
print(response.choices[0].message.content)
```

### curl
```bash
curl https://xxxx.ngrok.io/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-..." \
  -d '{"model":"gemma","messages":[{"role":"user","content":"hello"}]}'
```

---

## Running the agent (interactive CLI)
The agent reads `GEMMA_URL` and `GEMMA_API_KEY` from `.env` automatically:
```bash
python agentic_immunology/agent/agent.py
```
- If ngrok is running → uses public URL (works from anywhere)
- If ngrok is off → falls back to SLURM node discovery (cluster-only)

## Running tests
```bash
cd agentic_immunology/server
bash test.sh   # or: python test.py
```

---

## Files in this folder

| File | Purpose |
|------|---------|
| `server_gemma4.sh` | SLURM job script — runs llama-server on GPU node |
| `start_ngrok.sh` | Starts ngrok tunnel, updates `.env` with public URL |
| `download_gemma4_27B.sh` | One-time model download (~21 GB) |
| `ngrok` | ngrok binary (static, no install needed) |
| `test.py` | Agent smoke test (routing + tool use) |
| `test.sh` | Wrapper: `python test.py` |
| `logs/` | SLURM job logs |

---

## Troubleshooting

**Model still loading (503)**  
Wait ~2 min after `sbatch` before starting ngrok. The model takes time to load into GPU memory.

**ngrok tunnel disconnects**  
Restart with `bash start_ngrok.sh` — `.env` will be updated with the new URL.

**401 Unauthorized**  
Wrong or missing API key. Check `GEMMA_API_KEY` in `.env`.

**SLURM job not found**  
`squeue -u $USER` — if expired, resubmit: `sbatch server_gemma4.sh`
