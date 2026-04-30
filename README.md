# Agentic Immunology

## 1. Install

Optionally create a dedicated environment (recommended: `iagent_env`):

**venv**
```bash
python3 -m venv iagent_env && source iagent_env/bin/activate
```

**conda**
```bash
conda create -n iagent_env python=3.11 -y && conda activate iagent_env
```

Then install the package. From the main repo, call:
```bash
bash install.sh
```

## 2. Run the integrated agent:

activate the env where you installed the repo (e.g. iagent_env)
```bash
python agent/agent.py
```

