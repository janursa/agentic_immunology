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


MAIN_DIR          = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AGENT_DIR         = os.path.join(MAIN_DIR, "agent")
TEMP_DIR          = os.path.join(MAIN_DIR, "temp")
INSTRUCTIONS_FILE = os.path.join(MAIN_DIR, "egad.md")

# Provider — "gemma" (local OpenAI-compatible server) or "openai" (official API).
# Set LLM_PROVIDER=openai in .env to switch; everything below follows from it.
LLM_PROVIDER = _get("LLM_PROVIDER", "gemma").lower()

# Connection — read from .env, fallback to cluster-local address
GEMMA_URL     = _get("GEMMA_URL", f"http://localhost:8080/v1")
GEMMA_API_KEY = _get("GEMMA_API_KEY", "none")
SERVER_PORT   = 8080

if LLM_PROVIDER == "openai":
    BASE_URL   = _get("LLM_BASE_URL", "")          # empty -> OpenAI SDK default endpoint
    API_KEY    = _get("OPENAI_API_KEY", "none")
    MODEL_NAME = _get("LLM_MODEL", "gpt-4o-mini")
else:
    BASE_URL   = _get("LLM_BASE_URL", GEMMA_URL)
    API_KEY    = _get("LLM_API_KEY", GEMMA_API_KEY)
    MODEL_NAME = _get("LLM_MODEL", "gemma")

MAX_TOKENS      = 3000
TEMPERATURE     = 0.3
MAX_TOOL_ROUNDS = 30
TOOL_TIMEOUT    = 120

ALLOWED_WRITE_PREFIXES = [
    os.path.join(MAIN_DIR, "temp") + os.sep,
    os.path.join(MAIN_DIR, "agent") + os.sep,
]
BLOCKED_COMMANDS = [
    "rm -rf", "rm -f /", "mkfs", "dd if=",
    ":(){ :|:&};:", "> /dev/sda",
]

