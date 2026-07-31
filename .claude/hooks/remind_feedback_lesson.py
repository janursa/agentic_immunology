#!/usr/bin/env python3
"""PreToolUse hook (matcher: Agent): if a design.md/report.md was just
presented to the user via serve_dashboard.sh (marked by
mark_awaiting_feedback.py) and the orchestrator is now dispatching again —
meaning the user's response already happened, since the workflow always
stops and waits after presenting — remind it to document the feedback and
note whether a lesson was captured. Non-blocking: injects additionalContext,
does not deny the call. Fires once per marker (deleted after reminding).

Run from the repo root:
    python3 .claude/hooks/remind_feedback_lesson.py --self-test
"""
import json
import os
import pathlib
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))


def marker_path(session_id: str) -> pathlib.Path:
    return PROJECT_DIR / "temp" / ".hook_state" / f"{session_id}_awaiting_feedback.json"


def build_reminder(task: str, stage: str) -> str:
    return (
        f"Reminder (ciim_agentic.md 'How to process user feedback'): you presented "
        f"temp/{task}/{stage}.html for review and are now dispatching again, so the "
        f"user's response already happened. Confirm it was logged to "
        f"temp/{task}/feedback_log/{stage}/feedback.md (presented content + comments). "
        f"If it yielded a lesson, log it with `python memory/memory_blob.py add "
        f"--issue-tag <tag> --agents <agent1,agent2> --task {task} --lesson \"Situation: ... "
        f"Lesson: ...\"` (NOT Claude's auto-memory folder) after confirming with the user; "
        f"otherwise note 'Lesson: none'."
    )


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    session_id = data.get("session_id", "")
    path = marker_path(session_id)
    try:
        marker = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return
    path.unlink(missing_ok=True)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": build_reminder(marker.get("task", "?"), marker.get("stage", "?")),
        }
    }))


def _demo() -> None:
    text = build_reminder("x", "design")
    assert "temp/x/design.html" in text and "feedback_log/design/feedback.md" in text

    import tempfile
    global PROJECT_DIR
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        path = marker_path("sess1")
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"task": "x", "stage": "design", "ts": "now"}))
        assert path.exists()
        marker = json.loads(path.read_text())
        path.unlink()
        assert not path.exists()
        assert marker["task"] == "x"
    PROJECT_DIR = real_project_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
