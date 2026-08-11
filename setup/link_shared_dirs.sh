#!/usr/bin/env bash
# Symlinks datalake/ subfolders, singularity/, and the Claude Code agents into place.
# Safe to re-run any time (e.g. after a fresh checkout).
set -euo pipefail
cd "$(dirname "$0")/.."

CIIM_DATALAKE=/vol/projects/CIIM/agentic/datalake
CIIM_SINGULARITY=/vol/projects/CIIM/singularity

mkdir -p datalake
for d in "$CIIM_DATALAKE"/*/; do
  name=$(basename "$d")
  ln -sfn "$CIIM_DATALAKE/$name" "datalake/$name"
done

rm -rf singularity
ln -s "$CIIM_SINGULARITY" singularity

rm -rf .claude/agents
mkdir -p .claude/agents
ln -s ../../ciim_agentic.md .claude/agents/ciim_agentic.md
for f in agents/*.md; do
  ln -s "../../$f" ".claude/agents/$(basename "$f")"
done

echo "Linked datalake/*, singularity/, and .claude/agents/ to CIIM/repo sources."
