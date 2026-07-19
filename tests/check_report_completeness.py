#!/usr/bin/env python3
"""
Tier 0 checker: does report.md cite every file actually generated under
temp/{task}/? Deterministic, no LLM involved — reusable standalone (manual
audit of a finished task) or from the Tier 1 report probe (see
tests/tier1_probes.md).

Run with:
    python3 agentic_immunology/tests/check_report_completeness.py <task_dir>
    python3 agentic_immunology/tests/check_report_completeness.py --self-test
"""
import argparse
import pathlib
import sys
import tempfile


def missing_files(task_dir: pathlib.Path) -> list:
    report_path = task_dir / "report.md"
    if not report_path.exists():
        raise FileNotFoundError(f"no report.md under {task_dir}")
    text = report_path.read_text()
    actual = [p for p in task_dir.rglob("*") if p.is_file() and p.resolve() != report_path.resolve()]
    return sorted(p for p in actual if str(p.resolve()) not in text)


def _self_test() -> None:
    print("\n[check_report_completeness self-test]")
    with tempfile.TemporaryDirectory() as d:
        task_dir = pathlib.Path(d)
        (task_dir / "code").mkdir()
        (task_dir / "results" / "images").mkdir(parents=True)
        script = task_dir / "code" / "script.py"
        fig = task_dir / "results" / "images" / "fig1.png"
        csv = task_dir / "results" / "data.csv"
        for f in (script, fig, csv):
            f.write_text("x")

        (task_dir / "report.md").write_text(
            f"Generated files:\n- {script.resolve()}\n- {fig.resolve()}\n- {csv.resolve()}\n"
        )
        missing = missing_files(task_dir)
        assert missing == [], f"expected no missing files, got {missing}"
        print("  \033[92m✓ PASS\033[0m  complete report reports zero missing files")

        (task_dir / "report.md").write_text(
            f"Generated files:\n- {script.resolve()}\n- {fig.resolve()}\n"
        )
        missing = missing_files(task_dir)
        assert missing == [csv.resolve()], f"expected [{csv.resolve()}], got {missing}"
        print("  \033[92m✓ PASS\033[0m  incomplete report flags the omitted csv")
    print("RESULT: All self-tests passed ✓")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("task_dir", nargs="?", help="e.g. temp/my_task/")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()

    if args.self_test:
        _self_test()
        return

    if not args.task_dir:
        p.error("task_dir is required unless --self-test")

    task_dir = pathlib.Path(args.task_dir)
    missing = missing_files(task_dir)
    if missing:
        print(f"MISSING from report.md ({len(missing)}):")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    print(f"OK: report.md at {task_dir / 'report.md'} covers every generated file.")
    sys.exit(0)


if __name__ == "__main__":
    main()
