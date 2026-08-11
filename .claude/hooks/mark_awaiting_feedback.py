#!/usr/bin/env python3
"""PostToolUse hook (matcher: Bash): when scripts/serve_dashboard.sh is called
with a path (i.e. a design.md/findings.md review is being presented to the
user, per ciim_agentic.md's "Interact with user"), record a marker so the
next Agent dispatch can remind the orchestrator to document the feedback
that follows (see remind_feedback_lesson.py). Non-blocking, informational
only — see check_dashboard_url_relayed.py for the harder-block sibling of this
pattern.

Run from the repo root:
    python3 .claude/hooks/mark_awaiting_feedback.py --self-test
"""
import json
import os
import pathlib
import re
import sys
from datetime import datetime, timezone

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
SERVE_RE = re.compile(r"serve_dashboard\.sh\s+([^\s&|;]+)")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def parse_task_stage(path: str) -> tuple[str, str] | None:
    rel = path.strip("'\"")
    rel = rel[2:] if rel.startswith("./") else rel
    rel = rel[len("temp/"):] if rel.startswith("temp/") else rel
    parts = rel.split("/")
    if len(parts) < 2:
        return None  # no task segment, e.g. bare "design.html"
    task = parts[0]
    stage = pathlib.Path(parts[-1]).stem
    return task, stage


def marker_path(session_id: str) -> pathlib.Path:
    return PROJECT_DIR / "temp" / ".hook_state" / f"{session_id}_awaiting_feedback.json"


def write_marker(session_id: str, task: str, stage: str) -> None:
    path = marker_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"task": task, "stage": stage, "ts": _now()}))


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return
    command = data.get("tool_input", {}).get("command", "")
    match = SERVE_RE.search(command)
    if not match:
        return
    parsed = parse_task_stage(match.group(1))
    if parsed is None:
        return
    task, stage = parsed
    session_id = data.get("session_id", "")
    if session_id:
        write_marker(session_id, task, stage)


def _demo() -> None:
    assert parse_task_stage("temp/x/design.html") == ("x", "design")
    assert parse_task_stage("x/report.html") == ("x", "report")
    assert parse_task_stage("./temp/abf300/report.html") == ("abf300", "report")
    assert parse_task_stage("design.html") is None  # no task segment

    m = SERVE_RE.search("bash scripts/serve_dashboard.sh temp/x/design.html")
    assert m and m.group(1) == "temp/x/design.html"
    assert SERVE_RE.search("bash scripts/serve_dashboard.sh") is None  # no-arg base-URL form

    import tempfile
    global PROJECT_DIR
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        write_marker("sess1", "x", "design")
        marker = json.loads(marker_path("sess1").read_text())
        assert marker["task"] == "x" and marker["stage"] == "design"
    PROJECT_DIR = real_project_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
