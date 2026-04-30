#!/usr/bin/env bash

PYTHON="iagent_env/bin/python3"

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: 'iagent_env' not found. See README for setup instructions."
    exit 1
fi

exec "$PYTHON" "agent/agent.py" "$@"
