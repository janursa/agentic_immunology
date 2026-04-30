#!/bin/bash
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
singularity exec \
  --bind /vol/projects:/vol/projects \
  "${REPO_DIR}/singularity/biomni_full.sif" \
  python3 "${REPO_DIR}/tests/test_infer_tf_activity.py"
