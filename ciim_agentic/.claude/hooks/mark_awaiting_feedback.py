#!/usr/bin/env python3
"""PostToolUse hook (matcher: Bash): when scripts/serve_dashboard.sh is called
with a path (i.e. a design.md/findings.md review is being presented to the
user, per ciim_agentic.md's "Interact with user"), record a marker (including
the served .html path, so capture_feedback.py can find and attach the
sibling .md content that was actually shown) so the user's next message is
captured as feedback and sent to memory_bank. Non-blocking, informational only — see
check_dashboard_url_relayed.py for the harder-block sibling of this pattern.

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
    # A model's command text may use the literal, unexpanded "${CIIM_TEMP_DIR}/"
    # token (hooks see the raw command string, not the shell-expanded one), the
    # bare "temp/" shorthand (the historical default, still common regardless of
    # override), or the fully resolved value (relative or an absolute override).
    resolved_prefix = os.environ.get("CIIM_TEMP_DIR", "temp").rstrip("/") + "/"
    rel = path.strip("'\"")
    rel = rel[2:] if rel.startswith("./") else rel
    for prefix in ("${CIIM_TEMP_DIR}/", "$CIIM_TEMP_DIR/", "temp/", resolved_prefix):
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    parts = rel.split("/")
    if len(parts) < 2:
        return None  # no task segment, e.g. bare "design.html"
    task = parts[0]
    stage = pathlib.Path(parts[-1]).stem
    return task, stage


def marker_path(session_id: str) -> pathlib.Path:
    temp = os.environ.get("CIIM_TEMP_DIR", "temp")
    return PROJECT_DIR / temp / ".hook_state" / f"{session_id}_awaiting_feedback.json"


def write_marker(session_id: str, task: str, stage: str, html_path: str) -> None:
    path = marker_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"task": task, "stage": stage, "html_path": html_path, "ts": _now()}))


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return
    command = data.get("tool_input", {}).get("command", "")
    match = SERVE_RE.search(command)
    if not match:
        return
    html_arg = match.group(1)
    parsed = parse_task_stage(html_arg)
    if parsed is None:
        return
    task, stage = parsed
    session_id = data.get("session_id", "")
    if session_id:
        write_marker(session_id, task, stage, html_arg.strip("'\""))


def _demo() -> None:
    assert parse_task_stage("temp/x/design.html") == ("x", "design")
    assert parse_task_stage("x/report.html") == ("x", "report")
    assert parse_task_stage("./temp/abf300/report.html") == ("abf300", "report")
    assert parse_task_stage("design.html") is None  # no task segment
    assert parse_task_stage("${CIIM_TEMP_DIR}/memtest/design.html") == ("memtest", "design")
    assert parse_task_stage("$CIIM_TEMP_DIR/memtest/design.html") == ("memtest", "design")

    m = SERVE_RE.search("bash scripts/serve_dashboard.sh temp/x/design.html")
    assert m and m.group(1) == "temp/x/design.html"
    assert SERVE_RE.search("bash scripts/serve_dashboard.sh") is None  # no-arg base-URL form

    import tempfile
    global PROJECT_DIR
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        write_marker("sess1", "x", "design", "temp/x/design.html")
        marker = json.loads(marker_path("sess1").read_text())
        assert marker["task"] == "x" and marker["stage"] == "design"
        assert marker["html_path"] == "temp/x/design.html"
    PROJECT_DIR = real_project_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
