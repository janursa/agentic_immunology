#!/usr/bin/env bash
# Installs egad_host.md as the /egad-host slash command for this repo.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p .claude/commands
# ponytail: symlink, not a copy — editing egad_host.md is the install
ln -sfn ../../egad_host.md .claude/commands/egad-host.md
echo "installed: $PWD/.claude/commands/egad-host.md -> egad_host.md"

# egad's agents, alongside the host's own. list.md/models.yaml are indexes, not agents.
mkdir -p .claude/agents
for f in ../egad/agents/*.md; do
  b=$(basename "$f")
  [ "$b" = list.md ] && continue
  ln -sfn "../../$f" ".claude/agents/$b"
  echo "  agent: $b"
done

# drop symlinks whose target went away
find .claude/agents .claude/commands -xtype l -print -delete

echo "restart claude (or /exit) and type /egad-host"
