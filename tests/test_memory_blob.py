"""
Tier 0 unit tests for knowhow/memory_blob.py — the feedback-capture store
every subagent's "Past lessons for you:" injection is built from.

Run with:
    python3 agentic_immunology/tests/test_memory_blob.py
"""
import sys
import os
import json
import tempfile
import pathlib

_KNOWHOW_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'knowhow'))
sys.path.insert(0, _KNOWHOW_DIR)
import memory_blob as mb  # noqa: E402

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"


def check(condition, msg):
    status = PASS if condition else FAIL
    print(f"  {status}  {msg}")
    if not condition:
        raise AssertionError(msg)


def _fixture(tmpdir):
    """Point memory_blob's module-level file paths at an isolated fixture so
    tests never touch the real knowhow/memory_blob.jsonl."""
    tmp = pathlib.Path(tmpdir)
    tags = tmp / "issue_tags.json"
    blob = tmp / "memory_blob.jsonl"
    listmd = tmp / "list.md"
    tags.write_text(json.dumps({"stat_approach": "statistical method issues"}))
    blob.write_text("")
    listmd.write_text(
        "| `data_analyst_agent` | sonnet | ... |\n"
        "| `study_designer_agent` | sonnet | ... |\n"
    )
    mb.TAGS_FILE = tags
    mb.BLOB_FILE = blob
    mb.LIST_FILE = listmd


def test_add_then_retrieve_round_trip():
    print("\n[test_add_then_retrieve_round_trip]")
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        entry = mb.add_entry(
            "stat_approach", ["data_analyst_agent"], "aging_clock_task",
            "Situation: used wrong cohort. Lesson: check age distribution first.",
        )
        check(entry["issue_tag"] == "stat_approach", "issue_tag stored correctly")
        check(entry["agents"] == ["data_analyst_agent"], "agents stored correctly")
        check(entry["source"] == "HUMAN", "source defaults to HUMAN")
        got = mb.retrieve(agent="data_analyst_agent")
        check(len(got) == 1, "retrieve by agent returns the entry")
        check(got[0]["lesson"] == entry["lesson"], "retrieved lesson matches what was stored")


def test_retrieve_filters_by_agent_and_tag():
    print("\n[test_retrieve_filters_by_agent_and_tag]")
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        mb.add_entry("stat_approach", ["data_analyst_agent"], "task_a", "Situation: a. Lesson: a.")
        mb.add_entry("stat_approach", ["study_designer_agent"], "task_b", "Situation: b. Lesson: b.")
        check(len(mb.retrieve(agent="data_analyst_agent")) == 1, "filters out unrelated agent's entry")
        check(len(mb.retrieve(agent="study_designer_agent")) == 1, "returns the other agent's entry")
        check(len(mb.retrieve(issue_tag="stat_approach")) == 2, "issue_tag filter returns both")
        check(len(mb.retrieve(agent="nonexistent_agent")) == 0, "unknown agent returns nothing")


def test_rejects_unknown_tag():
    print("\n[test_rejects_unknown_tag]")
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        raised = False
        try:
            mb.add_entry("not_a_real_tag", ["data_analyst_agent"], "t", "Situation: x. Lesson: y.")
        except ValueError:
            raised = True
        check(raised, "unknown issue_tag raises ValueError")


def test_rejects_unknown_agent():
    print("\n[test_rejects_unknown_agent]")
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        raised = False
        try:
            mb.add_entry("stat_approach", ["not_a_real_agent"], "t", "Situation: x. Lesson: y.")
        except ValueError:
            raised = True
        check(raised, "unknown agent raises ValueError")


def test_rejects_missing_situation_or_lesson():
    print("\n[test_rejects_missing_situation_or_lesson]")
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        raised = False
        try:
            mb.add_entry("stat_approach", ["data_analyst_agent"], "t", "just a plain sentence with no structure.")
        except ValueError:
            raised = True
        check(raised, "lesson missing Situation:/Lesson: structure raises ValueError")


def test_rejects_overlong_lesson():
    print("\n[test_rejects_overlong_lesson]")
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        long_lesson = "Situation: " + ("word " * 60) + ". Lesson: " + ("word " * 60) + "."
        raised = False
        try:
            mb.add_entry("stat_approach", ["data_analyst_agent"], "t", long_lesson)
        except ValueError:
            raised = True
        check(raised, "lesson over MAX_LESSON_WORDS raises ValueError")


def test_comma_space_in_agents_is_rejected():
    print("\n[test_comma_space_in_agents_is_rejected]")
    # Regression: ciim_agentic.md's example command used to read
    # `--agents <agent1, agent2>`. The space survives argparse's comma-split
    # and memory_blob.py never strips it, so the second agent silently fails
    # validation instead of registering. This locks in today's strict
    # behavior so a future doc edit can't reintroduce the footgun unnoticed.
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        agents_arg = "data_analyst_agent, study_designer_agent"  # simulates argparse's raw --agents value
        agents = agents_arg.split(",")
        check(
            agents == ["data_analyst_agent", " study_designer_agent"],
            "split(',') leaves a leading space on the second agent",
        )
        raised = False
        try:
            mb.add_entry("stat_approach", agents, "t", "Situation: x. Lesson: y.")
        except ValueError:
            raised = True
        check(raised, "unstripped agent name (' study_designer_agent') is rejected, not silently accepted")


def test_add_tag_rejects_duplicate():
    print("\n[test_add_tag_rejects_duplicate]")
    with tempfile.TemporaryDirectory() as d:
        _fixture(d)
        raised = False
        try:
            mb.add_tag("stat_approach", "duplicate of an existing tag")
        except ValueError:
            raised = True
        check(raised, "add_tag refuses to overwrite an existing tag")


if __name__ == '__main__':
    print("=" * 60)
    print("memory_blob.py — Tier 0 Test Suite")
    print("=" * 60)

    tests = [
        test_add_then_retrieve_round_trip,
        test_retrieve_filters_by_agent_and_tag,
        test_rejects_unknown_tag,
        test_rejects_unknown_agent,
        test_rejects_missing_situation_or_lesson,
        test_rejects_overlong_lesson,
        test_comma_space_in_agents_is_rejected,
        test_add_tag_rejects_duplicate,
    ]

    failed = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed.append((t.__name__, str(e)))
        except Exception as e:
            failed.append((t.__name__, f"Unexpected error: {type(e).__name__}: {e}"))

    print("\n" + "=" * 60)
    if failed:
        print(f"RESULT: {len(failed)}/{len(tests)} tests FAILED")
        for name, msg in failed:
            print(f"  - {name}: {msg}")
        sys.stdout.flush()
        sys.exit(1)
    else:
        print(f"RESULT: All {len(tests)} tests passed ✓")
        sys.stdout.flush()
        sys.exit(0)
