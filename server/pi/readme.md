# Pi Coding Agent — Installation & Setup

Pi is a minimal terminal-based coding harness that supports 15+ AI providers.
Homepage: https://pi.dev/

## Installation

Node.js is available via the `py10` conda environment's `nodeenv`. Install pi globally with:

```bash
npm install -g @mariozechner/pi-coding-agent
```

Binary lands at: `~/.nvm` or (in this setup) `/home/jnourisa/miniconda3/envs/py10/envs/nodeenv/bin/pi`

## Configuration

Pi stores its config in `~/.pi/agent/`. Two files matter:

### `~/.pi/agent/models.json`
Defines custom providers. The `gemma-local` provider points to the llama-server running on the cluster:

```json
{
  "providers": {
    "gemma-local": {
      "baseUrl": "http://bioinf040:8080/v1",
      "api": "openai-completions",
      "apiKey": "<GEMMA_API_KEY from agentic_immunology/.env>",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        {
          "id": "unsloth_gemma-4-26B-A4B-it-GGUF_UD-Q5_K_M.gguf",
          "name": "Gemma4 26B (local)",
          "reasoning": false,
          "contextWindow": 32768,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

### `~/.pi/agent/config.json`
Sets the active model:

```json
{
  "model": "unsloth_gemma-4-26B-A4B-it-GGUF_UD-Q5_K_M.gguf"
}
```

## The Gemma Server

The backend is a `llama-server` SLURM job defined in `server/server_gemma4.sh`. It runs on a GPU node and exposes an OpenAI-compatible API on port 8080. The node hostname changes per job — update `baseUrl` in `models.json` whenever the server is restarted on a new node. The current hostname is always printed in the job log:

```
Connect from any node with:
  base_url = 'http://<hostname>:8080/v1'
```

The API key and current URL are stored in `agentic_immunology/.env`:

```
GEMMA_URL=http://bioinf040:8080/v1
GEMMA_API_KEY=...
```

## Usage

```bash
pi   # interactive TUI, will use the configured gemma-local provider
```

To explicitly select the provider/model:

```bash
pi --provider gemma-local --model unsloth_gemma-4-26B-A4B-it-GGUF_UD-Q5_K_M.gguf
```
