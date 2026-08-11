#!/usr/bin/env python3
"""Archive a finished analysis: move temp/{task}/ -> past_analysis/{task}/ and append
one index line to past_analysis/index.jsonl.

User-gated — the orchestrator runs this only after the user agrees to document the run.

    python scripts/archive_analysis.py <task> --prompt "..." --level L2 \
        --datasets abf300,SI --finding "..." --finding "..." [--verdict ACCEPT]

Run the self-test with: python scripts/archive_analysis.py --self-test
"""
import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMP = ROOT / "temp"
ARCHIVE = ROOT / "past_analysis"
INDEX = ARCHIVE / "index.jsonl"


def archive(task, prompt, level, datasets, findings, verdict, temp=TEMP, archive_dir=ARCHIVE):
    src = temp / task
    dst = archive_dir / task
    if not src.is_dir():
        sys.exit(f"error: {src} does not exist")
    if dst.exists():
        sys.exit(f"error: {dst} already exists — archive it under a different task name")
    archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    entry = {
        "task": task,
        "date": datetime.date.today().isoformat(),
        "level": level,
        "prompt": prompt,
        "datasets": datasets,
        "findings": findings,
        "verdict": verdict,
        "dir": str(dst),
        "report": str(dst / "findings.md") if (dst / "findings.md").exists() else None,
        "design": str(dst / "design.md") if (dst / "design.md").exists() else None,
    }
    with (archive_dir / "index.jsonl").open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def main():
    p = argparse.ArgumentParser()
    p.add_argument("task", nargs="?")
    p.add_argument("--prompt", help="the user's original prompt, verbatim")
    p.add_argument("--level", choices=["L0", "L1", "L2", "L3"])
    p.add_argument("--datasets", default="", help="comma-separated dataset names used")
    p.add_argument("--finding", action="append", default=[], help="repeatable, 3-5 total")
    p.add_argument("--verdict", default="ACCEPT")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not (a.task and a.prompt and a.level and a.finding):
        p.error("task, --prompt, --level and at least one --finding are required")
    entry = archive(a.task, a.prompt, a.level,
                    [d for d in a.datasets.split(",") if d], a.finding, a.verdict)
    print(json.dumps(entry, indent=2))
    print(f"\narchived: {entry['dir']}\nindexed:  {INDEX}")


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tmp, arc = Path(d) / "temp", Path(d) / "past_analysis"
        (tmp / "demo").mkdir(parents=True)
        (tmp / "demo" / "findings.md").write_text("x")
        e = archive("demo", "why?", "L2", ["si"], ["found y"], "ACCEPT", tmp, arc)
        assert not (tmp / "demo").exists(), "source not moved"
        assert (arc / "demo" / "findings.md").read_text() == "x"
        assert e["report"].endswith("past_analysis/demo/findings.md")
        assert e["design"] is None
        lines = (arc / "index.jsonl").read_text().splitlines()
        assert len(lines) == 1 and json.loads(lines[0])["task"] == "demo"
    print("self-test ok")


if __name__ == "__main__":
    main()
