#!/bin/bash
#SBATCH --job-name=nourisa
#SBATCH --partition=gpu
#SBATCH --nodelist=bioinf034
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=20G
#SBATCH --cpus-per-task=8
#SBATCH --time=30-00:00:00
#SBATCH --qos=verylong
#SBATCH --output=logs/gemma4_server/server_%j.log

echo "========================================"
echo "  Gemma 4 26B-A4B Server (Unsloth UD-Q5_K_M)"
echo "  Node    : $(hostname)"
echo "  Port    : 8080"
echo "  Started : $(date)"
echo "  Job ID  : ${SLURM_JOB_ID}"
echo "========================================"
echo ""
echo "Connect from any node with:"
echo "  base_url = 'http://$(hostname):8080/v1'"
echo ""

MODEL=/home/jnourisa/.cache/llama.cpp/unsloth_gemma-4-26B-A4B-it-GGUF_UD-Q5_K_M.gguf
ENV_FILE=/vol/projects/CIIM/agentic_central/.env

# Read API key from .env
API_KEY=$(grep '^GEMMA_API_KEY=' "$ENV_FILE" | cut -d'=' -f2-)

singularity exec --nv \
    --bind /vol/projects:/vol/projects \
    --bind /home/jnourisa:/home/jnourisa \
    --env LD_LIBRARY_PATH=/app \
    /vol/projects/CIIM/agentic_central/singularity/gemma4.sif \
    llama-server \
        -m "${MODEL}" \
        --host 0.0.0.0 \
        --port 8080 \
        --ctx-size 32768 \
        --n-gpu-layers 99 \
        --no-warmup \
        --api-key "${API_KEY}"
