#!/bin/bash
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
singularity exec \
  --bind /vol/projects:/vol/projects \
  "${REPO_DIR}/singularity/ciim.sif" \
  python3 "${REPO_DIR}/tests/test_aging_clock.py"
