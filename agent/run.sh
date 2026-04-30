#!/usr/bin/env bash
# Run the Gemma immunology agent using a shared virtualenv.
# The venv is on the shared filesystem — accessible on all nodes for all users.
# Running outside a container avoids nested singularity issues when the agent
# calls 'singularity exec' for tool scripts.
#
# Usage:
#   bash run.sh                          # auto-discover server
#   bash run.sh --server bioinf025:8080  # specify server explicitly

exec /vol/projects/BIIM/agentic_central/agent_venv/bin/python3 \
  /vol/projects/BIIM/agentic_central/agent/agent.py "$@"
