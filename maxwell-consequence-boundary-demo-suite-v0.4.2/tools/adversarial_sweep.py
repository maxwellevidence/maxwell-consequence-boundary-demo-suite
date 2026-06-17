from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path

SWEEP_VERSION = "maxwell-adversarial-sweep-v0.4.0"


def run(cmd: list[str], cwd: Path, env: dict[str, str], timeout: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return 124, output + f"\nTIMEOUT after {timeout}s\n"
    return proc.returncode, proc.stdout


def run_demo(demo: Path, timeout: int, keep_artifacts: bool) -> dict:
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    env["PYTHONPATH"] = "src"
    code, output = run(["make", "adversarial"], demo, env, timeout=timeout)
    result = {
        "demo": demo.name,
        "returncode": code,
        "passed": code == 0,
        "output_tail": output[-4000:],
    }
    if not keep_artifacts:
        clean_code, clean_output = run(["make", "clean"], demo, env, timeout=timeout)
        result["clean_returncode"] = clean_code
        if clean_code != 0:
            result["passed"] = False
            result["clean_output_tail"] = clean_output[-4000:]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the public adversarial corpus for every Maxwell demo.")
    parser.add_argument("root", nargs="?", default=".", help="Suite root")
    parser.add_argument("--json", dest="json_out", default="", help="Optional JSON report path")
    parser.add_argument("--keep-artifacts", action="store_true", help="Do not run make clean after each demo")
    parser.add_argument("--timeout", type=int, default=120, help="Per-demo timeout in seconds")
    parser.add_argument("--jobs", type=int, default=4, help="Parallel demo jobs")
    parser.add_argument("--only", default="", help="Comma-separated demo directory names or prefixes to run")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    demos_dir = root / "demos"
    if not demos_dir.exists():
        print(f"{SWEEP_VERSION}: missing demos directory: {demos_dir}", file=sys.stderr)
        return 2

    all_demos = [p for p in sorted(demos_dir.iterdir()) if p.is_dir() and (p / "Makefile").exists()]
    if len(all_demos) != 10:
        print(f"{SWEEP_VERSION}: expected 10 demo directories, found {len(all_demos)}", file=sys.stderr)
        return 2
    if args.only:
        tokens = [item.strip() for item in args.only.split(",") if item.strip()]
        demos = [d for d in all_demos if any(d.name == token or d.name.startswith(token) for token in tokens)]
        if not demos:
            print(f"{SWEEP_VERSION}: --only matched no demos: {args.only}", file=sys.stderr)
            return 2
    else:
        demos = all_demos

    print(f"{SWEEP_VERSION}: running {len(demos)} demo adversarial targets with jobs={args.jobs}, timeout={args.timeout}s", flush=True)
    results_by_name: dict[str, dict] = {}
    if args.jobs <= 1:
        for demo in demos:
            result = run_demo(demo, args.timeout, args.keep_artifacts)
            results_by_name[demo.name] = result
            status = "PASS" if result.get("passed") else "FAIL"
            print(f"==> {status}: {demo.name}", flush=True)
            if not result.get("passed"):
                print(result.get("output_tail", ""), flush=True)
                if result.get("clean_output_tail"):
                    print(result["clean_output_tail"], flush=True)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
            future_map = {executor.submit(run_demo, demo, args.timeout, args.keep_artifacts): demo for demo in demos}
            for future in concurrent.futures.as_completed(future_map):
                demo = future_map[future]
                try:
                    result = future.result()
                except Exception as exc:  # pragma: no cover - defensive for CLI harness
                    result = {"demo": demo.name, "returncode": 99, "passed": False, "output_tail": f"harness exception: {exc}"}
                results_by_name[demo.name] = result
                status = "PASS" if result.get("passed") else "FAIL"
                print(f"==> {status}: {demo.name}", flush=True)
                if not result.get("passed"):
                    print(result.get("output_tail", ""), flush=True)
                    if result.get("clean_output_tail"):
                        print(result["clean_output_tail"], flush=True)

    results = [results_by_name[d.name] for d in demos]
    failures = [r["demo"] for r in results if not r.get("passed")]
    report = {
        "sweep_version": SWEEP_VERSION,
        "suite_root": str(root),
        "demo_count": len(demos),
        "passed": not failures,
        "failures": failures,
        "results": results,
    }
    if args.json_out:
        out = Path(args.json_out)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote adversarial sweep JSON report to {out}", flush=True)

    if failures:
        print(f"{SWEEP_VERSION}: FAILED: {', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"{SWEEP_VERSION}: passed for {len(demos)} demos.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
