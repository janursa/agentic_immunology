#!/usr/bin/env bash
# Wires this repo's agent files into .claude/agents/ via symlinks.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf .claude/agents
mkdir -p .claude/agents

ln -s ../../ciim_agentic.md .claude/agents/ciim_agentic.md
for f in agents/*.md; do
  ln -s "../../$f" ".claude/agents/$(basename "$f")"
done
