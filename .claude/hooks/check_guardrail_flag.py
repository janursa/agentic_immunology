#!/usr/bin/env python3
"""PreToolUse hook: enforce ciim_agentic.md's Delegation HARD RULES on every
Agent tool call, so a dropped requirement is a hard stop, not a hoped-for
convention.

1. GUARDRAIL flag — peer_reviewer_agent in DESIGN-REVIEW/METHOD-REVIEW mode,
   and every data_analyst_agent call, must state "GUARDRAIL: on/off" verbatim.
2. output_conventions.md — every call to an analysis subagent
   (data_analyst_agent, data_download_agent) must append
   knowhow/output_conventions.md's full contents verbatim.
3. Past lessons — before dispatching to any agent listed in agents/list.md,
   if knowhow/memory_blob.jsonl has entries for that agent, the prompt must
   include "Past lessons for you:" plus each stored lesson verbatim.

Run from the repo root:
    python3 .claude/hooks/check_guardrail_flag.py --self-test
"""
import json
import os
import pathlib
import re
import subprocess
import sys

GUARDRAIL_RE = re.compile(r"GUARDRAIL:\s*(on|off)\b")

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
OUTPUT_CONVENTIONS_FILE = PROJECT_DIR / "knowhow" / "output_conventions.md"
MEMORY_BLOB_SCRIPT = PROJECT_DIR / "knowhow" / "memory_blob.py"
LIST_FILE = PROJECT_DIR / "agents" / "list.md"

ANALYSIS_AGENTS = {"data_analyst_agent", "data_download_agent"}


def block_reason(subagent_type: str, prompt: str) -> str | None:
    if GUARDRAIL_RE.search(prompt):
        return None
    if subagent_type == "data_analyst_agent":
        return (
            "data_analyst_agent requires 'GUARDRAIL: on' or 'GUARDRAIL: off' "
            "verbatim in the task prompt (ciim_agentic.md HARD RULE)."
        )
    if subagent_type == "peer_reviewer_agent" and re.search(
        r"DESIGN-REVIEW|METHOD-REVIEW", prompt
    ):
        return (
            "peer_reviewer_agent in DESIGN-REVIEW/METHOD-REVIEW mode requires "
            "'GUARDRAIL: on' or 'GUARDRAIL: off' verbatim in the task prompt "
            "(ciim_agentic.md HARD RULE)."
        )
    return None


def _conventions_block_reason(conventions_text: str, subagent_type: str, prompt: str) -> str | None:
    if subagent_type not in ANALYSIS_AGENTS or not conventions_text:
        return None
    if conventions_text not in prompt:
        return (
            f"{subagent_type} call must append the full contents of "
            "knowhow/output_conventions.md verbatim to the task prompt "
            "(ciim_agentic.md HARD RULE)."
        )
    return None


def block_reason_conventions(subagent_type: str, prompt: str) -> str | None:
    try:
        conventions_text = OUTPUT_CONVENTIONS_FILE.read_text().strip()
    except OSError:
        return None  # ponytail: fail-open if the file's missing, don't block on infra
    return _conventions_block_reason(conventions_text, subagent_type, prompt)


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
    try:
        return set(re.findall(r"\|\s*`([a-zA-Z_]+)`\s*\|", LIST_FILE.read_text()))
    except OSError:
        return set()


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


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    tool_input = data.get("tool_input", {})
    subagent_type = tool_input.get("subagent_type", "")
    prompt = tool_input.get("prompt", "")
    reason = (
        block_reason(subagent_type, prompt)
        or block_reason_conventions(subagent_type, prompt)
        or block_reason_lessons(subagent_type, prompt)
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
    # 1. GUARDRAIL flag (unchanged behavior)
    assert block_reason("data_analyst_agent", "do the analysis") is not None
    assert block_reason("data_analyst_agent", "GUARDRAIL: on\ndo it") is None
    assert block_reason("peer_reviewer_agent", "MODE: RESULTS-REVIEW") is None
    assert block_reason("peer_reviewer_agent", "MODE: DESIGN-REVIEW") is not None
    assert (
        block_reason("peer_reviewer_agent", "MODE: METHOD-REVIEW\nGUARDRAIL: off")
        is None
    )
    assert block_reason("study_designer_agent", "design the study") is None

    # 2. output_conventions.md verbatim
    conv = "## Output conventions\n...\n"
    assert _conventions_block_reason(conv, "data_analyst_agent", "do it") is not None
    assert _conventions_block_reason(conv, "data_analyst_agent", "do it\n" + conv) is None
    assert _conventions_block_reason(conv, "study_designer_agent", "no conventions needed") is None
    assert _conventions_block_reason("", "data_analyst_agent", "anything") is None  # fail-open, no file

    # 3. past lessons verbatim
    entries = [{"lesson": "Situation: x. Lesson: check the cohort age spread."}]
    assert _lessons_block_reason([], "no lessons exist, nothing required") is None
    assert _lessons_block_reason(entries, "do the analysis") is not None  # section missing entirely
    assert _lessons_block_reason(entries, "Past lessons for you:\n- something else") is not None  # section present, lesson text absent
    assert _lessons_block_reason(
        entries, "Past lessons for you:\n- Situation: x. Lesson: check the cohort age spread."
    ) is None

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
