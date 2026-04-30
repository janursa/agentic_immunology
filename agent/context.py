"""Builds the system prompt: instructions file + session context."""

import os
from config import INSTRUCTIONS_FILE


def build_system_prompt(session_dir: str) -> str:
    instructions = _read(INSTRUCTIONS_FILE)

    behaviour = """
---
## This Session
Session workspace: SESSION_DIR_PLACEHOLDER
---
## How to behave

**Think before responding.**
Before writing your reply, reason through: what does the user actually need?
What data/tools are relevant? What is the simplest correct approach?

**For multi-step tasks: plan first, then ask.**
Briefly describe what you will do (a few bullets), then ask "Shall I proceed?"
and wait for confirmation before running scripts or submitting jobs.
Once confirmed, execute fully — do not stop for each sub-step.

**For simple lookups or questions: just answer.**
Use tools if needed, then reply directly. No plan needed.

**Handle errors yourself.**
Handle the errors raised from your own code. If that belongs to the agentic system, surface the error.

"""

    behaviour = behaviour.replace("SESSION_DIR_PLACEHOLDER", session_dir)
    return instructions + behaviour


def _read(path: str) -> str:
    if not os.path.isfile(path):
        return f"(instructions file not found: {path})"
    with open(path, errors="replace") as f:
        return f.read()
