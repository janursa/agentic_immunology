# Gemma 4 Local Server

Runs **Gemma 4 E4B** (4B parameter instruction-tuned model) as a persistent OpenAI-compatible
HTTP server on a cluster GPU node via SLURM. Any node on the cluster can then call it like
a normal API.

---

## Files

| File | Purpose |
|---|---|
| `server.sh` | SLURM job script — launches the llama-server on a GPU node |
| `wait_and_test.py` | Monitors the job, waits for the server to come online, runs a scripted or interactive test |
| `test_client.py` | Standalone client for manual testing (requires host/port) |
| `logs/` | SLURM output logs (`server_<jobid>.log`) — contains the node hostname |

---

## Quick Start

### 1. Submit the server job
```bash
sbatch /vol/projects/CIIM/agentic_central/server/gemma4/server.sh
# → note the job ID printed, e.g. "Submitted batch job 10219185"
```

### 2. Wait for it to start and run the test
```bash
cd /vol/projects/CIIM/agentic_central/server/gemma4
python3 wait_and_test.py --job <JOB_ID>
```
This polls SLURM until the job is RUNNING, reads the node from the log, waits for the HTTP
server to be ready, then runs a 3-turn immunology conversation test.

For an **interactive chat** session:
```bash
python3 wait_and_test.py --job <JOB_ID> --interactive
# type 'reset' to start a new topic, 'quit' to exit
```

### 3. Use it from any node / script
Once running, find the node from the log:
```bash
grep "Connect from" logs/server_<JOB_ID>.log
# → base_url = 'http://bioinf025:8080/v1'
```

Then call it like any OpenAI-compatible API:
```python
from openai import OpenAI

client = OpenAI(base_url="http://<NODE>:8080/v1", api_key="none")

conversation = []
conversation.append({"role": "user", "content": "Your question here"})

response = client.chat.completions.create(
    model="gemma",
    messages=conversation,
    max_tokens=1024,   # ⚠️ see note below — keep ≥ 1024
    temperature=0.7,
)
reply = response.choices[0].message.content
conversation.append({"role": "assistant", "content": reply})  # keep history for follow-ups
```

---

## Infrastructure

| Item | Detail |
|---|---|
| **Singularity image** | `/vol/projects/CIIM/agentic_central/singularity/gemma4.sif` |
| **Image base** | `nvidia/cuda:12.3.2-devel-ubuntu22.04` + llama.cpp built from source |
| **Model file** | `~/.cache/llama.cpp/ggml-org_gemma-4-E4B-it-GGUF_gemma-4-E4B-it-Q4_K_M.gguf` (~5 GB, Q4_K_M quant) |
| **SLURM partition** | `gpu`, 1 GPU, 40 GB RAM, 24-hour limit |
| **Compatible nodes** | All GPU nodes: bioinf023–026 (T4/V100), bioinf034 (A100), bioinf040–041 (H100) |
| **Server port** | 8080 |
| **API format** | OpenAI-compatible (`/v1/chat/completions`, `/v1/models`) |

---

## Important Considerations

### ⚠️ Always use `max_tokens ≥ 1024`
Gemma 4 uses an internal **reasoning/thinking chain** before generating its final answer.
This reasoning consumes tokens first (stored in `reasoning_content`, not `content`).
If `max_tokens` is too low (e.g. 200–300), the model exhausts the budget on reasoning and
returns an **empty `content`** field. Use `max_tokens=1024` as a minimum; `2048` for complex
questions.

### Multi-turn conversation management
The server is **stateless** — it has no memory between requests. You must maintain the full
conversation list yourself and pass it with every call (as shown above). Use `reset` in
interactive mode or clear the list in code to start a fresh topic.

### Job time limit
Each job runs for **24 hours** then expires. After expiry, just resubmit:
```bash
sbatch /vol/projects/CIIM/agentic_central/server/gemma4/server.sh
```
The model is cached locally so restart takes ~1 minute (no download).

### CUDA driver compatibility
The image is compiled with **CUDA 12.3** (`NATIVE=OFF`) and is compatible with the driver
on all cluster nodes (driver 545, CUDA 12.3). Do not replace the image with a pre-built
llama.cpp Docker image — those use CUDA 12.8+ which crashes on this cluster.

### GPU node availability
GPU nodes are shared. The job may queue for minutes to hours depending on cluster load.
Use `squeue -j <JOB_ID> --start` to check the estimated start time.
Use `wait_and_test.py` with `--timeout <seconds>` (default 3600) to wait longer:
```bash
python3 wait_and_test.py --job <JOB_ID> --timeout 86400  # wait up to 24h
```

### Model variants
The current setup uses `gemma-4-E4B-it-Q4_K_M` (~5 GB VRAM). Larger variants are available
from `ggml-org` on HuggingFace if needed:

| Model | VRAM | Best node |
|---|---|---|
| gemma-4-E2B-it-Q4_K_M | ~3 GB | any |
| **gemma-4-E4B-it-Q4_K_M** ← current | **~5 GB** | **any** |
| gemma-4-26B-A4B-it-Q4_K_M | ~14 GB | A100 / H100 |
| gemma-4-31B-it-Q4_K_M | ~20 GB | A100 / H100 |
