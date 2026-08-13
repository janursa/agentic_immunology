#!/usr/bin/env bash
# Fails if an agent definition or code file hardcodes a checkout-specific
# absolute path instead of resolving its own location at runtime.
# Docs (knowhow/, plans/, README, integration.md, ...) may legitimately
# mention these paths and are intentionally not scanned.
set -euo pipefail
cd "$(dirname "$0")/.."

PATTERN='/vol/projects/CIIM|/vol/projects/BIIM|/home/jnourisa/projs/ongoing'
DIRS='agents .pi/agents tools'

# excluded: datalake/singularity (data), *.log/*.out/*.err (generated run
# logs — legitimately record their own checkout's abs path), *.ipynb
# (notebooks mix exploratory/example paths, not enforced here)
if git grep -InE "$PATTERN" -- $DIRS '*.sh' '*.py' \
    ':!datalake' ':!singularity' ':!*.log' ':!*.out' ':!*.err' ':!*.ipynb'; then
  echo "" >&2
  echo "hardcoded checkout path found above — resolve it at runtime instead" >&2
  echo "(bash: \"\$(cd \"\$(dirname \"\${BASH_SOURCE[0]}\")\" && pwd)\", python: Path(__file__).resolve())" >&2
  exit 1
fi

echo "check_paths: clean"
