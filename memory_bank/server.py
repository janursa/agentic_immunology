#!/usr/bin/env python3
"""Raw feedback-interaction log server. Started manually:
    python3 memory_bank/server.py
Reads MEMORY_BANK_PORT / MEMORY_BANK_TOKENS from the repo-root .env
(MEMORY_BANK_TOKENS=user1:tok1,user2:tok2 — token identifies who sent it, so
a client can't just claim to be anyone). Tunneled for remote access via
start_ngrok.sh, which writes the public URL to MEMORY_BANK_URL in .env.
Stored records identify the sender by token, not the mapped name — the
name map exists only to reject unknown tokens, not to be persisted.

No curation here — POST /interactions just appends one raw JSON line to
memory_bank/interactions.jsonl. Turning that into memory_bank/memory_blob.jsonl
lessons (via memory_blob.py add) is still a separate, manual step; GET /lessons
serves those curated entries back out over HTTP so egad's own hooks never need
filesystem access into this host repo.

Run from the repo root:
    python3 memory_bank/server.py --self-test
"""
import json
import pathlib
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, request

import memory_blob

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


def build_record(token: str, body: dict) -> dict:
    return {
        "user": token,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "task_id": body.get("task_id", ""),
        "original_prompt": body.get("original_prompt", ""),
        "stage": body.get("stage", ""),
        "agents": body.get("agents", ""),
        "presented": body.get("presented", ""),
        "raw_text": body.get("raw_text", ""),
    }


def _bearer_token() -> str:
    return request.headers.get("Authorization", "").removeprefix("Bearer ").strip()


def _authorized_user() -> str | None:
    return token_user_map().get(_bearer_token())


@app.post("/interactions")
def add_interaction():
    token = _bearer_token()
    if token not in token_user_map():
        return jsonify(error="invalid token"), 401
    record = build_record(token, request.get_json(silent=True) or {})
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return jsonify(stored=True)


@app.get("/lessons")
def get_lessons():
    if not _authorized_user():
        return jsonify(error="invalid token"), 401
    agent = request.args.get("agent") or None
    return jsonify(entries=memory_blob.retrieve(agent=agent))


def _demo() -> None:
    global ENV_FILE, LOG_FILE
    import tempfile
    real_env_file, real_log_file = ENV_FILE, LOG_FILE
    real_tags_file, real_blob_file, real_list_files = memory_blob.TAGS_FILE, memory_blob.BLOB_FILE, memory_blob.LIST_FILES
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        ENV_FILE = tmp / ".env"
        ENV_FILE.write_text("MEMORY_BANK_TOKENS=alice:tok1,bob:tok2\n")
        LOG_FILE = tmp / "interactions.jsonl"
        memory_blob.TAGS_FILE = tmp / "issue_tags.json"
        memory_blob.BLOB_FILE = tmp / "memory_blob.jsonl"
        listmd = tmp / "list.md"
        listmd.write_text("| `data_analyst_agent` | sonnet | ... |\n")
        memory_blob.LIST_FILES = (listmd,)
        memory_blob.TAGS_FILE.write_text(json.dumps({"stat_approach": "x"}))
        memory_blob.BLOB_FILE.write_text("")

        assert token_user_map() == {"tok1": "alice", "tok2": "bob"}

        client = app.test_client()
        resp = client.post("/interactions", json={"raw_text": "hi"})
        assert resp.status_code == 401  # no token

        resp = client.post("/interactions",
                            json={"task_id": "x", "original_prompt": "find a novel target for immune aging",
                                  "presented": "## Plan\n...", "raw_text": "looks good"},
                            headers={"Authorization": "Bearer tok1"})
        assert resp.status_code == 200
        line = json.loads(LOG_FILE.read_text().splitlines()[0])
        assert line["user"] == "tok1" and line["task_id"] == "x" and line["raw_text"] == "looks good"
        assert line["presented"] == "## Plan\n..."
        assert line["original_prompt"] == "find a novel target for immune aging"

        resp = client.get("/lessons", query_string={"agent": "data_analyst_agent"})
        assert resp.status_code == 401  # no token

        memory_blob.add_entry("stat_approach", ["data_analyst_agent"], "t",
                               "Situation: x. Lesson: check the cohort age spread.")
        resp = client.get("/lessons", query_string={"agent": "data_analyst_agent"},
                           headers={"Authorization": "Bearer tok1"})
        assert resp.status_code == 200
        entries = resp.get_json()["entries"]
        assert len(entries) == 1 and "cohort age spread" in entries[0]["lesson"]
        resp = client.get("/lessons", query_string={"agent": "nobody_home"},
                           headers={"Authorization": "Bearer tok1"})
        assert resp.get_json()["entries"] == []
    ENV_FILE, LOG_FILE = real_env_file, real_log_file
    memory_blob.TAGS_FILE, memory_blob.BLOB_FILE, memory_blob.LIST_FILES = real_tags_file, real_blob_file, real_list_files
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        port = int(_env("MEMORY_BANK_PORT", "5055"))
        app.run(host="0.0.0.0", port=port)
