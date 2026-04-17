# Gemma 4 Server — LOG

## Goal
Install Gemma 4 (llama.cpp CUDA) in a Singularity image, run it on bioinf040 (H100),
and test multi-turn conversation via OpenAI-compatible API.

## Files
| File | Purpose |
|------|---------|
| `singularity/gemma4.def` | Singularity definition (llama.cpp CUDA Docker base) |
| `singularity/gemma4.sif` | Built image (built via sbatch) |
| `temp/gemma4_server/server.sh` | SLURM sbatch job to start server on bioinf040 |
| `temp/gemma4_server/test_client.py` | Python test client (scripted + interactive) |
| `temp/gemma4_server/logs/` | SLURM job logs |
| `temp/gemma4_server/hf_cache/` | HuggingFace model cache (GGUF weights) |

## Architecture
```
bioinf040 (H100 GPU, SLURM job)
  └─ singularity exec --nv gemma4.sif
       └─ llama-server (Gemma 4 E4B-it, port 8080, OpenAI API)
              ▲
              │ HTTP
              │
any node / login node
  └─ test_client.py  (openai Python client)
```

## Steps

### Step 1 — Build Singularity image
```bash
cd /vol/projects/CIIM/agentic_central/singularity
singularity build --fakeroot gemma4.sif gemma4.def
```

### Step 2 — Launch server on bioinf040
```bash
cd /vol/projects/CIIM/agentic_central/server/gemma4
sbatch server.sh
# Note job ID, check log for hostname + "server listening" message
tail -f logs/server_<JOBID>.log
```

### Step 3 — Test client
```bash
# Scripted test
python3 test_client.py --host bioinf040 --port 8080

# Interactive mode
python3 test_client.py --host bioinf040 --port 8080 --interactive
```

## Status
- [x] `gemma4.def` written (`ggml-org/llama.cpp:server-cuda` base)
- [x] `gemma4.sif` built (2.2 GB, `/vol/projects/CIIM/agentic_central/singularity/gemma4.sif`)
- [x] `server.sh` submitted — job **10208234**, estimated start ~17:13
- [ ] Server running
- [ ] Client test passed

## Notes
- All GPU nodes fully allocated at submission time — job queued by priority
- Server will land on whichever GPU node frees first (any GPU, partition=gpu)
