"""Agent configuration."""

MAIN_DIR          = "/vol/projects/CIIM/agentic_central"
AGENT_DIR         = f"{MAIN_DIR}/agent"
SESSIONS_INDEX    = f"{AGENT_DIR}/sessions.json"   # global cross-session history
TEMP_DIR          = f"{MAIN_DIR}/temp"
INSTRUCTIONS_FILE = f"{MAIN_DIR}/central_agentic.instructions.md"

SERVER_PORT     = 8080
MODEL_NAME      = "gemma"
MAX_TOKENS      = 3000    # keep ≥ 1024; Gemma 4 reasoning eats tokens before content
TEMPERATURE     = 0.3
MAX_TOOL_ROUNDS = 30      # tool calls per single model turn
TOOL_TIMEOUT    = 120     # seconds per bash command

ALLOWED_WRITE_PREFIXES = [
    f"{MAIN_DIR}/temp/",
    f"{MAIN_DIR}/agent/",
]
BLOCKED_COMMANDS = [
    "rm -rf", "rm -f /", "mkfs", "dd if=",
    ":(){ :|:&};:", "> /dev/sda",
]
