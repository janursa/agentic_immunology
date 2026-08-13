#!/usr/bin/env python3
"""Raw feedback-interaction log server. Started manually:
    python3 memory_bank/server.py
Reads MEMORY_BANK_PORT / MEMORY_BANK_TOKENS from the repo-root .env
(MEMORY_BANK_TOKENS=user1:tok1,user2:tok2 — token identifies who sent it, so
a client can't just claim to be anyone). Tunneled for remote access via
start_ngrok.sh, which writes the public URL to MEMORY_BANK_URL in .env.

No curation here — POST /interactions just appends one raw JSON line to
memory_bank/interactions.jsonl. Turning that into memory/memory_blob.jsonl
lessons is a separate, not-yet-built step.

Run from the repo root:
    python3 memory_bank/server.py --self-test
"""
import json
import pathlib
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, request

ROOT = pathlib.Path(__file__).parent.parent
ENV_FILE = ROOT / ".env"
LOG_FILE = pathlib.Path(__file__).parent / "interactions.jsonl"

app = Flask(__name__)


def _env(key: str, default: str = "") -> str:
    try:
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return default


def token_user_map() -> dict:
    out = {}
    for pair in _env("MEMORY_BANK_TOKENS").split(","):
        if ":" in pair:
            user, token = pair.split(":", 1)
            out[token.strip()] = user.strip()
    return out


def build_record(user: str, body: dict) -> dict:
    return {
        "user": user,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "task": body.get("task", ""),
        "stage": body.get("stage", ""),
        "agents": body.get("agents", ""),
        "presented": body.get("presented", ""),
        "raw_text": body.get("raw_text", ""),
    }


@app.post("/interactions")
def add_interaction():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    user = token_user_map().get(token)
    if not user:
        return jsonify(error="invalid token"), 401
    record = build_record(user, request.get_json(silent=True) or {})
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return jsonify(stored=True)


def _demo() -> None:
    global ENV_FILE, LOG_FILE
    import tempfile
    real_env_file, real_log_file = ENV_FILE, LOG_FILE
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        ENV_FILE = tmp / ".env"
        ENV_FILE.write_text("MEMORY_BANK_TOKENS=alice:tok1,bob:tok2\n")
        LOG_FILE = tmp / "interactions.jsonl"

        assert token_user_map() == {"tok1": "alice", "tok2": "bob"}

        client = app.test_client()
        resp = client.post("/interactions", json={"raw_text": "hi"})
        assert resp.status_code == 401  # no token

        resp = client.post("/interactions", json={"task": "x", "presented": "## Plan\n...", "raw_text": "looks good"},
                            headers={"Authorization": "Bearer tok1"})
        assert resp.status_code == 200
        line = json.loads(LOG_FILE.read_text().splitlines()[0])
        assert line["user"] == "alice" and line["task"] == "x" and line["raw_text"] == "looks good"
        assert line["presented"] == "## Plan\n..."
    ENV_FILE, LOG_FILE = real_env_file, real_log_file
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        port = int(_env("MEMORY_BANK_PORT", "5055"))
        app.run(host="0.0.0.0", port=port)
