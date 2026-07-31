#!/usr/bin/env python3
"""PreToolUse hook (matcher: Write, Edit): block writes into Claude Code's
built-in auto-memory folder (~/.claude/projects/<slug>/memory/**). This
project has its own feedback store (memory/memory_blob.py, per
ciim_agentic.md 'How to process user feedback') and the two systems have been
confused before — the orchestrator once wrote a feedback lesson into the
auto-memory folder instead of calling memory_blob.py. Deny and redirect.

Run from the repo root:
    python3 .claude/hooks/block_global_memory_writes.py --self-test
"""
import json
import os
import pathlib
import re
import sys

AUTO_MEMORY_RE = re.compile(r"/\.claude/projects/[^/]+/memory/")

REASON = (
    "Writes into Claude Code's auto-memory folder (~/.claude/projects/.../memory/) "
    "are blocked in this project. Feedback/lessons belong in memory/memory_blob.py "
    "(`python memory/memory_blob.py add --issue-tag <tag> --agents <agent1,agent2> "
    "--task <task> --lesson \"Situation: ... Lesson: ...\"`), per ciim_agentic.md "
    "'How to process user feedback'."
)


def block_reason(tool_name: str, file_path: str) -> str | None:
    if tool_name not in ("Write", "Edit"):
        return None
    if AUTO_MEMORY_RE.search(file_path.replace(os.sep, "/")):
        return REASON
    return None


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    file_path = data.get("tool_input", {}).get("file_path", "")
    reason = block_reason(tool_name, file_path)
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))


def _demo() -> None:
    home_memory = str(pathlib.Path.home() / ".claude" / "projects" / "-home-x-y" / "memory" / "foo.md")
    assert block_reason("Write", home_memory) is not None
    assert block_reason("Edit", home_memory) is not None
    assert block_reason("Read", home_memory) is None  # only Write/Edit are blocked
    assert block_reason("Write", "memory/memory_blob.jsonl") is None  # project's own store
    assert block_reason("Write", "temp/x/feedback_log/design/feedback.md") is None
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
