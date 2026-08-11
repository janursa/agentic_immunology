#!/usr/bin/env python3
"""Deterministically copy phase n's '## Plan phase n' section out of design.md
into a standalone task.md for data_analyst_agent (ciim_agentic.md 'Execute'
step). Verbatim copy, no paraphrasing — the analyst's task can't drift from
what was actually reviewed and approved in design.md.

Usage:
    python3 scripts/extract_phase_task.py <design.md> <phase> <output task.md>
    python3 scripts/extract_phase_task.py --self-test
"""
import re
import sys
import pathlib


def extract_phase(design_text: str, phase: int) -> str:
    m = re.search(rf"^## Plan phase {phase}\b.*$", design_text, re.MULTILINE)
    if not m:
        raise ValueError(f"'## Plan phase {phase}' not found in design.md")
    rest = design_text[m.start():]
    nxt = re.search(r"^## ", rest[1:], re.MULTILINE)
    return rest if nxt is None else rest[: nxt.start() + 1]


def main() -> None:
    design_path, phase_s, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    section = extract_phase(pathlib.Path(design_path).read_text(), int(phase_s))
    pathlib.Path(out_path).write_text(section)
    print(f"Wrote {out_path}")


def _demo() -> None:
    text = (
        "## Overview\nx\n\n"
        "## Plan phase 0: Foo\n#### Execution plan\na\n\n"
        "## Plan phase 1: Bar\n#### Execution plan\nb\n\n"
        "## Rational behind phasing\nc\n"
    )
    p0 = extract_phase(text, 0)
    assert p0.startswith("## Plan phase 0: Foo") and "Execution plan\na" in p0 and "Plan phase 1" not in p0
    p1 = extract_phase(text, 1)
    assert p1.startswith("## Plan phase 1: Bar") and "Rational behind phasing" not in p1
    try:
        extract_phase(text, 9)
        assert False, "expected ValueError for a missing phase"
    except ValueError:
        pass
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
