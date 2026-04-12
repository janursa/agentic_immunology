#!/bin/bash

singularity exec \
  --bind /vol/projects:/vol/projects \
  /vol/projects/BIIM/agentic_central/singularity/ciim.sif \
  python3 /vol/projects/BIIM/agentic_central/tests/test_aging_clock.py
