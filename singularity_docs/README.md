# Biomni – Singularity Container

This folder contains everything needed to run [Biomni](https://github.com/snap-stanford/biomni), a general-purpose biomedical AI agent, inside a self-contained Singularity container — no local Python environment setup required.

---

## Files

| File | Description |
|------|-------------|
| `biomni_light.sif` | Pre-built container image (core Python stack) |
| `biomni_light.def` | Definition file used to build the light image |
| `biomni_full.def` | Definition file for the full image (adds bio tools: samtools, blast, scanpy, etc.) |
| `data/` | Pre-downloaded data lake (~15 GB) — downloaded once, never re-fetched |
| `build.sh` | Script to (re)build either image |
| `run.sh` | **Main entry point** — launches interactive or single-query mode |
| `run.py` | Python entry point called by `run.sh` |

---

## Prerequisites

- **Singularity / Apptainer** must be installed on your system. Check with:
  ```bash
  apptainer --version
  # or
  singularity --version
  ```
- An **OpenAI or Anthropic API key** (set as an environment variable before running).

> **Data lake:** The agent requires ~15 GB of reference data. This has already been pre-downloaded to `biomni/data/` and will be reused automatically on every run regardless of your working directory. No re-downloading will occur.

---

## Quick Start

### 1. Set your API key

```bash
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Launch the agent

**Interactive (chat) mode** — ask questions back and forth:

```bash
bash /vol/projects/CIIM/agentic_central/biomni/singularity/run.sh
```

**Single-query mode** — pass a question directly:

```bash
bash /vol/projects/CIIM/agentic_central/biomni/singularity/run.sh "What is the function of TP53?"
```

**Choose a specific model** (default is `gpt-4o-mini`):

```bash
bash /vol/projects/CIIM/agentic_central/biomni/singularity/run.sh --llm gpt-4o "Summarise CRISPR off-target detection methods."
```

---

## Interactive Session

Once in interactive mode you will see a prompt like:

```
======================================================================
  Biomni — General-Purpose Biomedical AI Agent
======================================================================

You can ask about:
  • Gene/protein function, variants, pathways
  • CRISPR screen design and analysis
  • scRNA-seq, bulk RNA-seq, ATAC-seq workflows
  • Literature retrieval and hypothesis generation
  • Any computational biology task

Type 'quit' or 'exit' to end the session.
======================================================================

You: _
```

Type your question and press Enter. Type `quit` or `exit` (or press `Ctrl+C`) to close the session.

---

## Choosing a Model

Pass `--llm <model>` to `run.sh` to select a model:

| Model string | Provider | Notes |
|---|---|---|
| `gpt-4o-mini` | OpenAI | Default — fast and cost-effective |
| `gpt-4o` | OpenAI | More capable |
| `claude-sonnet-4-5` | Anthropic | Balanced |
| `claude-opus-4-5` | Anthropic | Most capable |

---

## Example Tasks

```bash
# Gene function
bash run.sh "What is the role of BRCA1 in homologous recombination?"

# CRISPR design
bash run.sh "Design a CRISPR screen to identify genes involved in drug resistance in K562 cells."

# scRNA-seq workflow
bash run.sh "Outline a standard Seurat workflow for clustering a 10x PBMC dataset."

# Variant interpretation
bash run.sh "List TP53 variants associated with Li-Fraumeni syndrome and summarise their clinical significance."

# Omics analysis guidance
bash run.sh "How do I integrate scRNA-seq and ATAC-seq data from the same cells using WNN?"
```

---

## Building the Images

If you need to rebuild the images (e.g., after updating the definition files):

```bash
cd /vol/projects/CIIM/agentic_central/biomni/singularity

# Build the light image (core stack only)
APPTAINER_TMPDIR=/tmp bash build.sh light

# Build the full image (adds samtools, blast, scanpy, scvi-tools, cellpose, etc.)
APPTAINER_TMPDIR=/tmp bash build.sh full

# Build both
APPTAINER_TMPDIR=/tmp bash build.sh all
```

Builds typically take **5–15 minutes** depending on network speed.

---

## Troubleshooting

**`FileNotFoundError` for SSL cert**  
The SSL cert is bound automatically by `run.sh`. If you call `singularity exec` manually, add:
```bash
--bind /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem:/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
```

**`ModuleNotFoundError: No module named 'biomni'`**  
Use `run.sh` which handles bind-mounts automatically. If running manually, add:
```bash
--bind /vol/projects/CIIM/agentic_central/biomni:/biomni
```

**`ERROR: No API key found`**  
Export your key before calling `run.sh`:
```bash
export OPENAI_API_KEY=sk-...
bash run.sh
```

**Interactive mode not responding to input**  
Make sure you are running in a terminal with a TTY (not inside a non-interactive script or `nohup`). For batch jobs, use single-query mode instead.
