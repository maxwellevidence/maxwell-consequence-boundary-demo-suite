#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import inspect
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HARNESS_VERSION = "maxwell-adversarial-harness-v0.4.0"


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 45) -> int:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), timeout=timeout, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if proc.stdout.strip():
            print(proc.stdout[-2000:], flush=True)
        return proc.returncode
    except subprocess.TimeoutExpired as exc:
        print(f"TIMEOUT after {timeout}s: {' '.join(cmd)}", flush=True)
        if exc.stdout:
            print(str(exc.stdout)[-2000:], flush=True)
        return 124


def run_adversarial_module(demo: Path) -> tuple[int, int, str]:
    test_path = demo / "tests" / "adversarial" / "test_adversarial_corpus.py"
    if not test_path.exists():
        return 2, 0, "missing tests/adversarial/test_adversarial_corpus.py"
    old_sys_path = list(sys.path)
    old_cwd = Path.cwd()
    old_env_pp = os.environ.get("PYTHONPATH")
    module_name = "adv_" + demo.name.replace("-", "_")
    try:
        os.chdir(demo)
        sys.path.insert(0, str(demo / "src"))
        sys.path.insert(0, str(demo))
        os.environ["PYTHONPATH"] = "src"
        spec = importlib.util.spec_from_file_location(module_name, test_path)
        if spec is None or spec.loader is None:
            return 2, 0, "could not load adversarial test module"
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        tests = [(name, getattr(module, name)) for name in dir(module) if name.startswith("test_") and callable(getattr(module, name))]
        ran = 0
        for name, fn in tests:
            sig = inspect.signature(fn)
            sink = io.StringIO()
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                if "tmp_path" in sig.parameters:
                    with tempfile.TemporaryDirectory(prefix="maxwell_adv_") as td:
                        fn(Path(td))
                else:
                    fn()
            ran += 1
        return 0, ran, f"ran {ran} adversarial test function(s)"
    except Exception as exc:
        return 1, 0, f"{exc.__class__.__name__}: {exc}"
    finally:
        os.chdir(old_cwd)
        sys.path[:] = old_sys_path
        if old_env_pp is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = old_env_pp
        # Avoid cross-demo module cache contamination.
        for key in list(sys.modules):
            if key.startswith("maxwell_") or key == module_name:
                sys.modules.pop(key, None)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0] if argv else ".").resolve()
    rows: list[dict] = []
    failures: list[str] = []

    def record(scope: str, check: str, code: int, extra: dict | None = None) -> None:
        ok = code == 0
        row = {"scope": scope, "check": check, "status": "passed" if ok else "failed", "return_code": code}
        if extra:
            row.update(extra)
        rows.append(row)
        print(f"[{'PASS' if ok else 'FAIL'}] {scope}: {check}", flush=True)
        if not ok:
            failures.append(f"{scope}: {check} returned {code}; {extra or {}}")

    code = run_cmd([sys.executable, "tools/suite_spec_check.py", "."], root, timeout=30)
    record("suite", "suite_spec_check", code)

    demos = sorted((root / "demos").glob("[0-9][0-9]-*"))
    for demo in demos:
        scope = demo.name
        adv_inputs = len(list((demo / "examples" / "adversarial_inputs").glob("*.json"))) if (demo / "examples" / "adversarial_inputs").exists() else 0
        code, ran, detail = run_adversarial_module(demo)
        record(scope, "adversarial_corpus_direct", code, {"adversarial_input_count": adv_inputs, "test_functions_ran": ran, "detail": detail})

    summary = {
        "checks": len(rows),
        "checks_passed": sum(1 for r in rows if r["status"] == "passed"),
        "checks_failed": sum(1 for r in rows if r["status"] == "failed"),
        "demos": len(demos),
        "adversarial_input_files": sum(r.get("adversarial_input_count", 0) for r in rows),
        "test_functions_ran": sum(r.get("test_functions_ran", 0) for r in rows),
        "result": "passed" if not failures else "failed",
    }
    report = {
        "report_version": HARNESS_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "public demo suite only; synthetic local inputs; no production systems",
        "summary": summary,
        "results": rows,
        "limitations": [
            "internal automated adversarial harness pass, not independent third-party red team",
            "public-safe synthetic inputs only",
            "does not test production deployments or external services",
            "does not claim exhaustive security proof",
        ],
    }
    out_path = root / "reports" / "adversarial_harness_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("All adversarial harness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
