#!/usr/bin/env python3
"""PreToolUse hook: control Agent delegations using GUARDRAIL flag.

peer_reviewer_agent in
DESIGN-REVIEW/METHOD-REVIEW mode, and every data_analyst_agent call, must
state "GUARDRAIL: on" or "GUARDRAIL: off" verbatim in the task prompt.
Enforced here so a dropped flag is a hard stop, not a hoped-for convention.
"""
import json
import re
import sys

GUARDRAIL_RE = re.compile(r"GUARDRAIL:\s*(on|off)\b")


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


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    tool_input = data.get("tool_input", {})
    reason = block_reason(
        tool_input.get("subagent_type", ""), tool_input.get("prompt", "")
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
    assert block_reason("data_analyst_agent", "do the analysis") is not None
    assert block_reason("data_analyst_agent", "GUARDRAIL: on\ndo it") is None
    assert block_reason("peer_reviewer_agent", "MODE: RESULTS-REVIEW") is None
    assert block_reason("peer_reviewer_agent", "MODE: DESIGN-REVIEW") is not None
    assert (
        block_reason("peer_reviewer_agent", "MODE: METHOD-REVIEW\nGUARDRAIL: off")
        is None
    )
    assert block_reason("study_designer_agent", "design the study") is None
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
