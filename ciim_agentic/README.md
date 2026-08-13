# ciim_agentic

Agentic immunology workflow: orchestrator (`ciim_agentic.md`), core subagents (`agents/`), tools, docs, and guardrail hooks for Claude Code.

Launch `claude` from **inside this directory** — `ciim_agentic/` is a self-contained Claude Code project (its own `.claude/hooks`, `.claude/settings.json`, `.claude/agents/`). It reads/writes the host project root (one level up, `${CIIM_MAIN_DIR}`) for everything it doesn't ship itself: `application/`, `memory_bank/`, `scripts/`, `past_analysis/`, and the host's own on-demand agents (`agents/curate_paper.md` etc).

## Not shipped

Two directories this framework depends on are **not** part of this repo — too large / cluster-specific to commit:

- the datalake — provisioned datasets (indexed by `docs/datalake.md`).
- the singularity image directory — `.sif` container images (indexed by `docs/images.md`); the *only* permitted way to run python/R (see `docs/images.md`).

Nothing here hardcodes a folder name for either. `setup/install.sh` reads their paths from `.env` and exposes them to every Claude Code session as `${CIIM_DATALAKE_DIR}` / `${CIIM_SINGULARITY_DIR}` — that's how docs and agent prompts reference them.

## Install

1. Add as a submodule of your host project, or clone directly:
   ```
   git submodule add <ciim_agentic-repo-url> ciim_agentic
   ```
   or 
   ```
   git clone <ciim_agentic-repo-url> 
   ```

2. `cp ciim_agentic/.env.example ciim_agentic/.env` and fill it in (see below).
3. `bash ciim_agentic/setup/install.sh`
4. `cd ciim_agentic && claude`

The install script:
- errors out if the `claude` CLI isn't installed
- echoes the resolved `CIIM_MAIN_DIR` / `CIIM_DATALAKE_DIR` / `CIIM_SINGULARITY_DIR` / `CIIM_TEMP_DIR`
- writes those into `.claude/settings.local.json` (`env` block, gitignored) — so `${CIIM_MAIN_DIR}` etc. resolve for every Bash call and hook
- symlinks `.claude/agents/` to ciim_agentic's own agents plus the host's own `agents/*.md` (e.g. `curate_paper.md`), so both are discoverable in the same session
- cleans up any leftover host-side wiring from before ciim_agentic became self-contained

## Agents

`agents/` here holds only the core study-execution loop: `study_designer_agent`, `peer_reviewer_agent`, `data_analyst_agent` (+ a test stub). `install.sh` also pulls in the host's own on-demand agents (`${CIIM_MAIN_DIR}/agents/*.md`) so Claude Code discovers all of them from one session.

## `.env`

| Variable | Meaning |
|---|---|
| `CIIM_DATALAKE_DIR` | Absolute path to the datalake |
| `CIIM_SINGULARITY_DIR` | Absolute path to the `.sif` image directory |
| `CIIM_TEMP_DIR` | Where the per-task workspace lives. Default `temp` — resolved to an absolute path under the host root by `install.sh` |
| `OPENGWAS_TOKEN` | OpenGWAS API (optional) |
| `NGROK_AUTHTOKEN` | Tunnel for the results dashboard (optional) (`server/`) |
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code auth (non-interactive installs) (optional) |
| `SYNAPSE_AUTH_TOKEN` | Synapse-hosted dataset downloads (optional) |
| `MEMORY_BANK_URL` | Feedback-capture server address (optional, see `memory_bank/README.md`) |
| `MEMORY_BANK_TOKEN` | Your identity on that server (optional) |

`MEMORY_BANK_TOKEN` is issued, not self-generated — request one from
jalil.nourisa@gmail.com to connect to the shared memory_bank server.

`.env` is gitignored — never commit it.

## scAnnotAgent

`ciim_agentic/scAnnotAgent/` is its own git submodule (scRNA QC/annotation pipeline) — see `ciim_agentic/scAnnotAgent/SKILL.md`. Clone with `git submodule update --init --recursive` from the host.
