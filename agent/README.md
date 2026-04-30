# Gemma Agent


## Quick Start

```bash
# Start the LLM server (if not running — check with: squeue -u $USER)
cd /vol/projects/CIIM/agentic_central/server
sbatch server_gemma4.sh

# Launch the agent (server is auto-discovered from SLURM)
cd /vol/projects/CIIM/agentic_central/agent
python agent.py

# Or specify the server explicitly
python agent.py --server bioinf025:8080
```

## How It Works

The agent is a fluid conversation loop — no rigid phases. On each turn:

1. Your message is sent to the model along with the full conversation history.
2. The model **uses tools** (read files, list directories, run commands) as many times as it needs.
3. When satisfied, it gives you a text response.

For **complex tasks**, the model naturally:
- Explores relevant data/tools, summarises what it found
- Proposes a plan and asks "Shall I proceed?"
- Once you confirm, executes fully in one go

For **simple questions**, it just answers — no plan needed.

Each session gets its own workspace at `temp/session_<timestamp>/` with a `LOG.md`.
A session summary is saved to `agent/sessions.json` on exit (visible next session as history).

## Commands

| Input | Action |
|---|---|
| Any prompt | Agent thinks, uses tools, responds |
| `history` | Print past session summaries |
| `reset` | Clear conversation history (keeps session memory) |
| `exit` / Ctrl-C | End session, save summary, quit |

## Files

```
agent/
├── agent.py       Main loop + GemmaAgent class
├── config.py      Server settings, safety constraints
├── context.py     Assembles system prompt (instructions + session history)
├── memory.py      Per-session workspace + cross-session history
├── tools.py       Tool definitions (OpenAI format) + execution
├── sessions.json  Auto-created cross-session history index
└── README.md
```

## Tools the Agent Can Use

| Tool | Description |
|---|---|
| `read_file` | Read any file (truncated at 8 000 chars) |
| `list_directory` | List directory (optionally recursive, 2 levels) |
| `run_command` | Run bash (max 120 s): sbatch, head, grep, python scripts, etc. |
| `write_file` | Write files — restricted to `temp/` and `agent/` only |
| `search_files` | Glob-search for files by pattern |

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `MAX_TOKENS` | 3000 | Keep ≥ 1024 — Gemma 4 reasoning chain eats tokens before the visible reply |
| `TEMPERATURE` | 0.3 | Lower = more deterministic; raise for brainstorming |
| `MAX_TOOL_ROUNDS` | 30 | Tool calls per turn |
| `TOOL_TIMEOUT` | 120 s | Max time per bash command |

## System Prompt Design

The system prompt contains only:
- `central_agentic.instructions.md` — full environment description (already references tools.md, datalake.md, etc.)
- Session workspace path
- Past session history (last 6 sessions)
- Behavioural guidelines (think first, plan big tasks, be concise)

The model reads `tools.md`, `datalake.md`, etc. **on demand** via `read_file` when they are
relevant to a task — keeping the context lean and always current.

## Notes

- **Server auto-discovery**: uses `squeue` to find `gemma4-server` job and extract the node hostname.
- **24-hour SLURM limit**: resubmit with `sbatch server_gemma4.sh`; model is cached (~5 GB in `~/.cache/llama.cpp/`).
- **`max_tokens ≥ 1024`**: Gemma 4 has an internal reasoning chain that runs before the visible response. Too-small values produce empty replies.
