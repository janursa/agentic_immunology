#!/usr/bin/env python3
"""UserPromptSubmit hook: inject the orchestrator's own memory-blob lessons.

egad.md's delegation rule runs `memory_blob.py retrieve --agent <name>`
only when dispatching to a subagent, so lessons tagged `orchestrator` were never
loaded — least of all at step 0 (interpretation), which happens before any Agent
call. This puts them in front of the orchestrator as each new prompt arrives.

# ponytail: injects on every prompt; ~0.5k chars today. If orchestrator lessons
# grow past ~10, move this to SessionStart (fires on startup/resume/compact).

Run from egad/:
    python3 .claude/hooks/inject_orchestrator_lessons.py --self-test
"""
import json
import os
import pathlib
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
# memory_bank/ lives at the host root (CIIM_MAIN_DIR), one level up from
# PROJECT_DIR (egad/, the launch dir).
MAIN_DIR = pathlib.Path(os.environ.get("CIIM_MAIN_DIR", str(PROJECT_DIR.resolve().parent)))
sys.path.insert(0, str(MAIN_DIR / "memory_bank"))


def build_context() -> str | None:
    try:
        from memory_blob import _format_for_prompt, retrieve
    except ImportError:
        return None  # ponytail: fail-open, a missing blob must never block a prompt
    entries = retrieve(agent="orchestrator")
    if not entries:
        return None
    return (
        "Past lessons for you (orchestrator, from memory_bank/memory_blob.jsonl):\n"
        + _format_for_prompt(entries)
    )


def main() -> None:
    json.load(sys.stdin)  # payload unused; consume it so the hook doesn't SIGPIPE
    context = build_context()
    if context:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }))


def _demo() -> None:
    context = build_context()
    assert context is not None, "no orchestrator lessons found in memory_bank/memory_blob.jsonl"
    assert context.startswith("Past lessons for you (orchestrator")
    assert "[" in context  # at least one "- [issue-tag] ..." line

    # the hook emits well-formed UserPromptSubmit JSON
    import io
    real_stdin, sys.stdin = sys.stdin, io.StringIO('{"prompt": "hi"}')
    real_stdout, sys.stdout = sys.stdout, io.StringIO()
    main()
    emitted, sys.stdin, sys.stdout = sys.stdout.getvalue(), real_stdin, real_stdout
    assert json.loads(emitted)["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
