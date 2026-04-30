"""Agent configuration — reads connection settings from .env"""

import os

def _read_env() -> dict:
    """Parse .env file into a dict (does not override real env vars)."""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    result = {}
    try:
        with open(os.path.normpath(env_path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, _, v = line.partition('=')
                    result[k.strip()] = v.strip()
    except (FileNotFoundError, PermissionError):
        pass
    return result

_env = _read_env()

def _get(key: str, default: str = "") -> str:
    """env var > .env file > default"""
    return os.environ.get(key) or _env.get(key) or default


MAIN_DIR          = "/vol/projects/CIIM/agentic_central"
AGENT_DIR         = f"{MAIN_DIR}/agent"
TEMP_DIR          = f"{MAIN_DIR}/temp"
INSTRUCTIONS_FILE = f"{MAIN_DIR}/central_agentic.instructions.md"

# Connection — read from .env, fallback to cluster-local address
GEMMA_URL     = _get("GEMMA_URL", f"http://localhost:8080/v1")
GEMMA_API_KEY = _get("GEMMA_API_KEY", "none")
SERVER_PORT   = 8080

MODEL_NAME      = "gemma"
MAX_TOKENS      = 3000
TEMPERATURE     = 0.3
MAX_TOOL_ROUNDS = 30
TOOL_TIMEOUT    = 120

ALLOWED_WRITE_PREFIXES = [
    f"{MAIN_DIR}/temp/",
    f"{MAIN_DIR}/agent/",
]
BLOCKED_COMMANDS = [
    "rm -rf", "rm -f /", "mkfs", "dd if=",
    ":(){ :|:&};:", "> /dev/sda",
]

