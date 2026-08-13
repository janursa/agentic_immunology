# Agentic Immunology

## 1. Install

Optionally create a dedicated environment (recommended: `iagent_env`):

**venv**
```bash
python3 -m venv iagent_env && source iagent_env/bin/activate
```

**conda**
```bash
conda create -n iagent_env python=3.11 -y && conda activate iagent_env
```

Then install the package. From the main repo, call:
```bash
bash setup/install.sh
```

Link the shared datalake/singularity images and wire up the Claude Code subagents (symlinks
`datalake/*`, `singularity/`, `egad.md`, and `agents/*.md` into `.claude/agents/`):
```bash
bash setup/link_shared_dirs.sh
```

`datalake/`, `singularity/`, and `.claude/agents/` are git-tracked symlinks into `/vol/projects/CIIM`
and this repo's own `agents/` folder — a normal `git clone` gives you working symlinks as long as
you have CIIM access. If a symlink ever goes stale (e.g. renamed CIIM folder, new agent added),
rerun the command above.

Set up API tokens:
```bash
cp .env.example .env
```
Then fill in `.env` — see [Environment / API tokens](#environment--api-tokens-env) below.

### Checkout layout

Anyone with CIIM access can clone their own checkout anywhere — the repo has no dependency on a
specific checkout location.

### Optional: run the same agents via `pi` instead of Claude Code

[`pi`](https://github.com/earendil-works/pi) is an alternative CLI agent runtime that can use OpenAI, the
GWDG academic-cloud endpoint, or any OpenAI-compatible endpoint instead of Claude models. `setup/setup_pi.sh`:
- installs `pi` (`npm install -g @earendil-works/pi-coding-agent`) if missing
- installs the subagent delegation extension into `~/.pi/agent/extensions/subagent`
- if `GWDG_API_KEY` is set (put it in `.env`, gitignored), registers the `gwdg` provider and its
  full model catalog in pi's own config (`~/.pi/agent/models.json`) — skipped otherwise
- regenerates `.pi/agents/*.md` from `agents/*.md` and `.pi/SYSTEM.md` from `egad.md`,
  translating Claude-style tool names/model aliases into pi's format (model per agent is set
  in `agents/models.yaml`, e.g. `gwdg/qwen3-coder-next` or `openai/gpt-4o` — edit that file and
  re-run the script to change it; the full list of available `gwdg/*` ids is documented in a
  comment at the top of `agents/models.yaml`)

Nothing under `agents/`, `agents/models.yaml`, or `egad.md` is written by this script —
only pi's own config under `~/.pi/agent/` and the generated `.pi/` folder are.

```bash
bash setup/setup_pi.sh
```

Launch it (uses `.pi/SYSTEM.md` as the project system prompt automatically):
```bash
pi --model gwdg/qwen3-coder-next   # or e.g. openai/gpt-4o (reads OPENAI_API_KEY from the environment)
```

Then delegate like you would with Claude Code's `Agent` tool, e.g. `Use the data_analyst_agent
subagent to ...`. Always include `agentScope: "both"` when the model calls the `subagent` tool
(the system prompt already instructs it to) — otherwise `pi` only looks at user-level agents
and won't find these project ones.

**Known limitation:** pi has no built-in `WebSearch`/`WebFetch` equivalent, so those tools are
dropped from the generated `.pi/agents/*.md` for agents that use them (`data_analyst_agent`,
`paper_extractor`, `peer_reviewer_agent`, `benchmark_judge`) — they run tool-degraded under pi
until a web-search extension is added.

Re-run `setup/setup_pi.sh` any time `agents/*.md`, `egad.md`, or `agents/models.yaml` change.

## Environment / API tokens (`.env`)

`agentic_immunology/.env` (gitignored, copy from `.env.example`) holds tokens read directly by
tool code:

- `GEMMA_URL` / `GEMMA_API_KEY` — internal Gemma 4 server (see `server/gemma4/`).
- `OPENGWAS_TOKEN` — JWT for `phewas_opengwas`/`run_mr(mode='opengwas')` (see `tools/ciim/genetics.md`).
  Expires ~2 weeks after issue. **To renew:** log in at https://api.opengwas.io/profile/ (free
  account), copy the JWT shown there, and replace the `OPENGWAS_TOKEN=` line in `.env`.
- `NGROK_AUTHTOKEN` — used by `server/` to expose local servers publicly.
- `GWDG_API_KEY` — only needed for the optional `pi` runtime (see below).


## Deprecated: Run the integrated agent:
activate the env where you installed the repo (e.g. iagent_env)
```bash
python agent/agent.py
```

