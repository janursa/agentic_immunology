#!/usr/bin/env python3
"""UserPromptSubmit hook: if the user's previous turn was a feedback-marked
serve_dashboard.sh review (marked by mark_awaiting_feedback.py), POST the raw
prompt text to memory_bank's API, alongside the design.md/findings.md content
that was actually presented (read verbatim off disk, not summarized) — so a
later curation pass has both sides of the exchange, not just the reply.
Nothing for the orchestrator to remember or compose. Replaces
remind_feedback_lesson.py, which asked the orchestrator to do this by hand.

Reads MEMORY_BANK_URL / MEMORY_BANK_TOKEN from egad/.env — this is the
client side of the connection (which server, whose identity), configured per
user of this repo. The server itself (memory_bank/server.py, its port, and
its token->user map) is host infra — see memory_bank/README.md. Fails open:
if unconfigured or unreachable, logs to stderr and does nothing else — never
blocks the prompt. Fires once per marker (deleted after sending, or on
failure — the workflow always keeps moving).

Run from the repo root:
    python3 .claude/hooks/capture_feedback.py --self-test
"""
import json
import os
import pathlib
import sys
import urllib.request

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
ENV_FILE = PROJECT_DIR / ".env"


def marker_path(session_id: str) -> pathlib.Path:
    temp = os.environ.get("CIIM_TEMP_DIR", "temp")
    return PROJECT_DIR / temp / ".hook_state" / f"{session_id}_awaiting_feedback.json"


def _env(key: str) -> str:
    try:
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return ""


def find_presented(html_path: str) -> str:
    """The .md actually shown to the user lives next to the served .html
    (render_review_artifact.py's convention — see docs/design_graphs.md)."""
    html_path = html_path.strip("'\"")
    if html_path.startswith("./"):
        html_path = html_path[2:]
    directory = (PROJECT_DIR / html_path).parent
    for name in ("design.md", "findings.md"):
        candidate = directory / name
        if candidate.is_file():
            return candidate.read_text()
    return ""


def send(url: str, token: str, record: dict) -> bool:
    req = urllib.request.Request(
        url.rstrip("/") + "/interactions",
        data=json.dumps(record).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def main() -> None:
    data = json.load(sys.stdin)
    session_id = data.get("session_id", "")
    path = marker_path(session_id)
    try:
        marker = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return
    path.unlink(missing_ok=True)

    url = _env("MEMORY_BANK_URL")
    token = _env("MEMORY_BANK_TOKEN")
    if not url or not token:
        print("capture_feedback: MEMORY_BANK_URL/MEMORY_BANK_TOKEN not set, skipping", file=sys.stderr)
        return

    record = {
        "task": marker.get("task", ""),
        "stage": marker.get("stage", ""),
        "presented": find_presented(marker.get("html_path", "")),
        "raw_text": data.get("prompt", ""),
    }
    if not send(url, token, record):
        print("capture_feedback: memory_bank unreachable, skipping", file=sys.stderr)


def _demo() -> None:
    global PROJECT_DIR, ENV_FILE
    import tempfile
    real_project_dir, real_env_file = PROJECT_DIR, ENV_FILE
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        ENV_FILE = PROJECT_DIR / ".env"

        # unconfigured .env -> treated as unset, no crash
        assert _env("MEMORY_BANK_URL") == ""

        ENV_FILE.write_text("MEMORY_BANK_URL=http://127.0.0.1:9\nMEMORY_BANK_TOKEN=tok\n")
        assert _env("MEMORY_BANK_URL") == "http://127.0.0.1:9"
        assert _env("MEMORY_BANK_TOKEN") == "tok"

        # unreachable server -> fails open, doesn't raise
        assert send("http://127.0.0.1:9", "tok", {"raw_text": "x"}) is False

        # marker lifecycle: written, read, consumed once
        path = marker_path("sess1")
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"task": "x", "stage": "design", "html_path": "temp/x/design.html", "ts": "now"}))
        assert json.loads(path.read_text())["task"] == "x"
        path.unlink()
        assert not path.exists()

        # find_presented reads the sibling design.md next to the served html
        (PROJECT_DIR / "temp" / "x").mkdir(parents=True)
        (PROJECT_DIR / "temp" / "x" / "design.md").write_text("## Plan\ncontent")
        assert find_presented("temp/x/design.html") == "## Plan\ncontent"
        assert find_presented("temp/y/missing.html") == ""
    PROJECT_DIR, ENV_FILE = real_project_dir, real_env_file
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
