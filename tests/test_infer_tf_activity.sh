#!/bin/bash

singularity exec \
  --bind /vol/projects:/vol/projects \
  /vol/projects/BIIM/agentic_central/singularity/biomni_full.sif \
  python3 /vol/projects/BIIM/agentic_central/tests/test_infer_tf_activity.py
