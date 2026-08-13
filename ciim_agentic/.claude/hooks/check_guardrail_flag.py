#!/usr/bin/env python3
"""PreToolUse hook: enforce ciim_agentic.md's Delegation HARD RULES on every
Agent tool call, so a dropped requirement is a hard stop, not a hoped-for
convention.

1. Past lessons — before dispatching to any agent (agents/list.md
   or the host's own agents/list.md), if memory_bank/memory_blob.jsonl has entries
   for that agent, the prompt must include "Past lessons for you:" plus each
   stored lesson verbatim.
2. LITERATURE flag — every study_designer_agent call must pass the current
   `LITERATURE: on`/`off` value from ciim_agentic.md's Flags section verbatim.

Run from the repo root:
    python3 .claude/hooks/check_guardrail_flag.py --self-test
"""
import json
import os
import pathlib
import re
import subprocess
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
# Host project root, one level up — where memory_bank/ and the host's own agents/
# live. ciim_agentic/ itself is PROJECT_DIR (the launch dir).
MAIN_DIR = pathlib.Path(os.environ.get("CIIM_MAIN_DIR", str(PROJECT_DIR.resolve().parent)))
MEMORY_BLOB_SCRIPT = MAIN_DIR / "memory_bank" / "memory_blob.py"
CORE_LIST_FILE = PROJECT_DIR / "agents" / "list.md"
HOST_LIST_FILE = MAIN_DIR / "agents" / "list.md"
ORCHESTRATOR_FILE = PROJECT_DIR / "ciim_agentic.md"


def _lessons_block_reason(entries: list, prompt: str) -> str | None:
    if not entries:
        return None
    if "Past lessons for you:" not in prompt:
        return (
            f"{len(entries)} stored lesson(s) exist for this agent in "
            "memory_blob.jsonl but the task prompt has no 'Past lessons for "
            "you:' section (ciim_agentic.md HARD RULE)."
        )
    missing = [e for e in entries if e["lesson"] not in prompt]
    if missing:
        return (
            f"{len(missing)} of {len(entries)} stored lesson(s) for this "
            "agent are not present verbatim in the task prompt "
            "(ciim_agentic.md HARD RULE)."
        )
    return None


def _registered_agents() -> set:
    names = set()
    for f in (CORE_LIST_FILE, HOST_LIST_FILE):
        try:
            names |= set(re.findall(r"\|\s*`([a-zA-Z_]+)`\s*\|", f.read_text()))
        except OSError:
            pass
    return names


def _retrieve_lessons(subagent_type: str) -> list:
    try:
        result = subprocess.run(
            [sys.executable, str(MEMORY_BLOB_SCRIPT), "retrieve",
             "--agent", subagent_type, "--format", "json"],
            capture_output=True, text=True, timeout=5,
        )
    except OSError:
        return []
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def block_reason_lessons(subagent_type: str, prompt: str) -> str | None:
    if subagent_type not in _registered_agents():
        return None
    return _lessons_block_reason(_retrieve_lessons(subagent_type), prompt)


def _literature_flag_value(text: str) -> str | None:
    match = re.search(r"`LITERATURE:\s*(on|off)`", text)
    return match.group(1) if match else None


def _literature_block_reason(flag_value: str | None, subagent_type: str, prompt: str) -> str | None:
    if subagent_type != "study_designer_agent" or flag_value is None:
        return None
    if f"LITERATURE: {flag_value}" not in prompt:
        return (
            f"study_designer_agent call must pass the current LITERATURE flag "
            f"('LITERATURE: {flag_value}') verbatim in the task prompt "
            "(ciim_agentic.md HARD RULE)."
        )
    return None


def block_reason_literature(subagent_type: str, prompt: str) -> str | None:
    try:
        text = ORCHESTRATOR_FILE.read_text()
    except OSError:
        return None  # ponytail: fail-open if the file's missing, don't block on infra
    return _literature_block_reason(_literature_flag_value(text), subagent_type, prompt)


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    tool_input = data.get("tool_input", {})
    subagent_type = tool_input.get("subagent_type", "")
    prompt = tool_input.get("prompt", "")
    reason = (
        block_reason_lessons(subagent_type, prompt)
        or block_reason_literature(subagent_type, prompt)
    )
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))


def _demo() -> None:
    # 1. past lessons verbatim
    entries = [{"lesson": "Situation: x. Lesson: check the cohort age spread."}]
    assert _lessons_block_reason([], "no lessons exist, nothing required") is None
    assert _lessons_block_reason(entries, "do the analysis") is not None  # section missing entirely
    assert _lessons_block_reason(entries, "Past lessons for you:\n- something else") is not None  # section present, lesson text absent
    assert _lessons_block_reason(
        entries, "Past lessons for you:\n- Situation: x. Lesson: check the cohort age spread."
    ) is None

    # 2. LITERATURE flag verbatim
    assert _literature_flag_value("- `LITERATURE: off` — controls ...") == "off"
    assert _literature_flag_value("no flag line here") is None
    assert _literature_block_reason("off", "study_designer_agent", "design this") is not None
    assert _literature_block_reason("off", "study_designer_agent", "LITERATURE: off\ndesign this") is None
    assert _literature_block_reason("on", "study_designer_agent", "LITERATURE: off\ndesign this") is not None
    assert _literature_block_reason("off", "data_analyst_agent", "no flag needed here") is None
    assert _literature_block_reason(None, "study_designer_agent", "no flag line, fail-open") is None

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
