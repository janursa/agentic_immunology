#!/usr/bin/env python3
"""Structured feedback store: memory/memory_blob.jsonl.

add      -> validate + append one lesson entry (orchestrator is the sole writer, source=HUMAN).
retrieve -> filter entries by agent and/or issue_tag (line-by-line, no full parse into memory).
add-tag  -> extend the fixed issue-tag taxonomy in memory/issue_tags.json.
"""
import argparse
import datetime
import json
import re
from pathlib import Path

MEMORY_DIR = Path(__file__).parent
TAGS_FILE = MEMORY_DIR / "issue_tags.json"
BLOB_FILE = MEMORY_DIR / "memory_blob.jsonl"
LIST_FILE = MEMORY_DIR.parent / "agents" / "list.md"
EXTRA_AGENTS = {"orchestrator"}
MAX_LESSON_WORDS = 100


def load_tags() -> dict:
    return json.loads(TAGS_FILE.read_text())


def load_agents() -> set:
    names = set(re.findall(r"\|\s*`([a-zA-Z_]+)`\s*\|", LIST_FILE.read_text()))
    return names | EXTRA_AGENTS


def add_entry(issue_tag: str, agents: list, task: str, lesson: str) -> dict:
    tags = load_tags()
    if issue_tag not in tags:
        raise ValueError(f"Unknown issue_tag '{issue_tag}'. Known: {sorted(tags)}. "
                          f"Use add-tag first if this is genuinely new.")
    valid_agents = load_agents()
    if not agents:
        raise ValueError("agents must be a non-empty list.")
    for a in agents:
        if a not in valid_agents:
            raise ValueError(f"Unknown agent '{a}'. Known: {sorted(valid_agents)}.")
    lower = lesson.lower()
    if "situation" not in lower or "lesson" not in lower:
        raise ValueError("lesson must contain both a 'situation:' and a 'lesson:' part, "
                          "e.g. 'Situation: <one sentence>. Lesson: <what was learned>.'")
    n_words = len(lesson.split())
    if n_words >= MAX_LESSON_WORDS:
        raise ValueError(f"lesson too long ({n_words} words, max {MAX_LESSON_WORDS}).")

    entry = {
        "issue_tag": issue_tag,
        "agents": agents,
        "task": task,
        "date": datetime.date.today().isoformat(),
        "source": "HUMAN",  # ponytail: only writer today; extend if another source starts writing
        "lesson": lesson.strip(),
    }
    with BLOB_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def retrieve(agent: str = None, issue_tag: str = None) -> list:
    if not BLOB_FILE.exists():
        return []
    out = []
    with BLOB_FILE.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if agent and agent not in entry["agents"]:
                continue
            if issue_tag and issue_tag != entry["issue_tag"]:
                continue
            out.append(entry)
    return out


def add_tag(tag: str, description: str) -> None:
    tags = load_tags()
    if tag in tags:
        raise ValueError(f"Tag '{tag}' already exists: {tags[tag]}")
    tags[tag] = description
    TAGS_FILE.write_text(json.dumps(tags, indent=2) + "\n")


def _format_for_prompt(entries: list) -> str:
    return "\n".join(f"- [{e['issue_tag']}] {e['lesson']}" for e in entries)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--issue-tag", required=True)
    a.add_argument("--agents", required=True, help="comma-separated agent names")
    a.add_argument("--task", required=True)
    a.add_argument("--lesson", required=True)

    r = sub.add_parser("retrieve")
    r.add_argument("--agent")
    r.add_argument("--issue-tag")
    r.add_argument("--format", choices=["text", "json"], default="text")

    t = sub.add_parser("add-tag")
    t.add_argument("--tag", required=True)
    t.add_argument("--description", required=True)

    args = p.parse_args()

    if args.cmd == "add":
        entry = add_entry(args.issue_tag, args.agents.split(","), args.task, args.lesson)
        print(json.dumps(entry))
    elif args.cmd == "retrieve":
        entries = retrieve(args.agent, args.issue_tag)
        print(_format_for_prompt(entries) if args.format == "text" else json.dumps(entries))
    elif args.cmd == "add-tag":
        add_tag(args.tag, args.description)
        print(f"added tag '{args.tag}'")
