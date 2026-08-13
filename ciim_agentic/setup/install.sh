#!/usr/bin/env bash
# Sets up ciim_agentic's own .claude/ (hooks/settings/agents already live here —
# nothing gets pushed into the host). Launch `claude` from inside ciim_agentic/
# to use it. Also pulls in the host's own on-demand agents (agents/*.md at the
# host root, e.g. curate_paper.md) so they're discoverable in the same session.
# Safe to re-run any time (e.g. after a fresh checkout).
set -euo pipefail

CIIM_AGENTIC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_DIR="$(dirname "$CIIM_AGENTIC_DIR")"
cd "$CIIM_AGENTIC_DIR"

if ! command -v claude >/dev/null 2>&1; then
  echo "error: 'claude' CLI not found — install Claude Code first: https://claude.com/claude-code" >&2
  exit 1
fi

ENV_FILE="$CIIM_AGENTIC_DIR/.env"
[ -f "$ENV_FILE" ] || { echo "error: $ENV_FILE not found — copy .env.example to .env and fill it in first" >&2; exit 1; }
set -a
source "$ENV_FILE"
set +a

: "${CIIM_DATALAKE_DIR:?set CIIM_DATALAKE_DIR in $ENV_FILE}"
: "${CIIM_SINGULARITY_DIR:?set CIIM_SINGULARITY_DIR in $ENV_FILE}"
CIIM_TEMP_DIR="${CIIM_TEMP_DIR:-temp}"
CIIM_TEMP_DIR="${CIIM_TEMP_DIR%/}"
# Resolved absolute — outputs live in the host tree (temp/, application/, ...),
# not inside ciim_agentic/, and CWD is now ciim_agentic/ itself.
if [[ "$CIIM_TEMP_DIR" != /* ]]; then
  CIIM_TEMP_DIR="$HOST_DIR/$CIIM_TEMP_DIR"
fi

echo "CIIM_MAIN_DIR=$HOST_DIR"
echo "CIIM_DATALAKE_DIR=$CIIM_DATALAKE_DIR"
echo "CIIM_SINGULARITY_DIR=$CIIM_SINGULARITY_DIR"
echo "CIIM_TEMP_DIR=$CIIM_TEMP_DIR"

# Undo any leftover wiring from the old launch-from-host model.
[ -L "$HOST_DIR/.claude/hooks" ] && rm "$HOST_DIR/.claude/hooks"
[ -L "$HOST_DIR/.claude/settings.json" ] && rm "$HOST_DIR/.claude/settings.json"
for f in ciim_agentic.md data_analyst_agent.md peer_reviewer_agent.md study_designer_agent.md; do
  [ -L "$HOST_DIR/.claude/agents/$f" ] && rm "$HOST_DIR/.claude/agents/$f"
done

# Discoverable agents: ciim_agentic's own + the host's own (curate_paper.md etc).
mkdir -p "$CIIM_AGENTIC_DIR/.claude/agents"
ln -sfn "../../ciim_agentic.md" "$CIIM_AGENTIC_DIR/.claude/agents/ciim_agentic.md"
for f in "$CIIM_AGENTIC_DIR"/agents/*.md; do
  [ -e "$f" ] || continue
  base="$(basename "$f")"
  [ "$base" = "list.md" ] && continue  # index doc, not a discoverable subagent
  ln -sfn "../../agents/$base" "$CIIM_AGENTIC_DIR/.claude/agents/$base"
done
for f in "$HOST_DIR"/agents/*.md; do
  [ -e "$f" ] || continue
  base="$(basename "$f")"
  [ "$base" = "list.md" ] && continue
  ln -sfn "../../../agents/$base" "$CIIM_AGENTIC_DIR/.claude/agents/$base"
done

# Expose env vars to every session launched from inside ciim_agentic/ (Bash
# tool calls, hooks) via settings.local.json's env block (untracked/per-checkout).
python3 - "$CIIM_AGENTIC_DIR/.claude/settings.local.json" "$HOST_DIR" "$CIIM_DATALAKE_DIR" "$CIIM_SINGULARITY_DIR" "$CIIM_TEMP_DIR" <<'PYEOF'
import json, sys

path, main_dir, datalake, singularity, temp = sys.argv[1:6]
try:
    with open(path) as f:
        cfg = json.load(f)
except FileNotFoundError:
    cfg = {}
cfg.setdefault("env", {}).update({
    "CIIM_MAIN_DIR": main_dir,
    "CIIM_DATALAKE_DIR": datalake,
    "CIIM_SINGULARITY_DIR": singularity,
    "CIIM_TEMP_DIR": temp,
})
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
PYEOF

mkdir -p "$CIIM_TEMP_DIR"

echo "ciim_agentic ready — launch \`claude\` from $CIIM_AGENTIC_DIR"
