from __future__ import annotations

import argparse
import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TARGET_TESTS = [
    "tests/test_effect_gate_artifacts.py::test_policy_derived_allow_creates_effect_records_but_pause_and_block_do_not",
    "tests/test_effect_gate_artifacts.py::test_verifier_detects_improper_effect_record_after_pause_or_block",
]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={"PYTHONPATH": "src", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", **dict(__import__("os").environ)},
    )


def plant_fail_open_bug(demo_root: Path) -> str:
    target = demo_root / "src" / "maxwell_effect_gate" / "artifact_writer.py"
    original = target.read_text(encoding="utf-8")
    mutated = original.replace(
        'if decision_receipt["decision"] == "allow":',
        'if decision_receipt["decision"] in {"allow", "pause", "block"}:  # DECOY_FAIL_OPEN: forbidden effect emission',
    )
    if original == mutated:
        raise RuntimeError("Could not plant decoy fail-open bug; target text was not found.")
    target.write_text(mutated, encoding="utf-8")
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            mutated.splitlines(keepends=True),
            fromfile="a/demos/02-effect-gate-public-preview/src/maxwell_effect_gate/artifact_writer.py",
            tofile="b/demos/02-effect-gate-public-preview/src/maxwell_effect_gate/artifact_writer.py",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a decoy fail-open proof against Demo 02.")
    parser.add_argument("root", nargs="?", default=".", help="Suite root")
    parser.add_argument("--report-dir", default=None, help="Optional report directory to write proof logs")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    source_demo = root / "demos" / "02-effect-gate-public-preview"
    if not source_demo.exists():
        print(f"Missing flagship demo: {source_demo}")
        return 2

    with tempfile.TemporaryDirectory(prefix="maxwell-decoy-fail-open-") as tmp:
        demo_copy = Path(tmp) / "02-effect-gate-public-preview"
        ignore = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".hypothesis", "*.pyc")
        shutil.copytree(source_demo, demo_copy, ignore=ignore)

        clean = run([sys.executable, "-m", "pytest", "-q", *TARGET_TESTS], demo_copy)
        patch = plant_fail_open_bug(demo_copy)
        fail = run([sys.executable, "-m", "pytest", "-q", *TARGET_TESTS], demo_copy)

    if clean.returncode != 0:
        print("Decoy proof failed: baseline targeted tests did not pass.")
        print(clean.stdout)
        return 1
    if fail.returncode == 0:
        print("Decoy proof failed: planted fail-open bug was not caught.")
        print(fail.stdout)
        return 1
    if "FAILED" not in fail.stdout and "failed" not in fail.stdout.lower():
        print("Decoy proof failed: expected pytest failure markers were not present.")
        print(fail.stdout)
        return 1

    if args.report_dir:
        report_dir = Path(args.report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "README.md").write_text(
            "# Decoy Fail-Open Regression Proof\n\n"
            "This directory records the v0.4.1 decoy-branch proof. A temporary copy of Demo 02 is patched "
            "so pause/block decisions incorrectly emit `effect_record.json`. The targeted tests must fail on "
            "that patched copy and pass on the unmodified copy.\n\n"
            "This is not an external audit. It proves the shipped harness catches one known fail-open regression class.\n",
            encoding="utf-8",
        )
        (report_dir / "fail_open_patch.diff").write_text(patch, encoding="utf-8")
        (report_dir / "restored_pass_log.txt").write_text(clean.stdout, encoding="utf-8")
        (report_dir / "expected_failure_log.txt").write_text(fail.stdout, encoding="utf-8")
        (report_dir / "summary.json").write_text(
            '{\n'
            '  "version": "v0.4.1",\n'
            '  "decoy_bug": "pause_and_block_emit_effect_record",\n'
            '  "baseline_targeted_tests_passed": true,\n'
            '  "patched_targeted_tests_failed_as_expected": true,\n'
            '  "claim": "The public harness catches this known fail-open regression class."\n'
            '}\n',
            encoding="utf-8",
        )

    print("Decoy fail-open proof passed: baseline tests passed, planted fail-open patch failed as expected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
