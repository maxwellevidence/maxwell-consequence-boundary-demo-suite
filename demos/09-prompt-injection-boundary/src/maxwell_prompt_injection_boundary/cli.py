from __future__ import annotations

import argparse
from pathlib import Path

from .engine import run_suite, verify_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Maxwell Prompt Injection Boundary Demo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    demo = sub.add_parser("demo")
    demo.add_argument("--inputs", required=True)
    demo.add_argument("--policy", required=True)
    demo.add_argument("--out", required=True)

    run_suite_cmd = sub.add_parser("run-suite")
    run_suite_cmd.add_argument("--input-dir", required=True)
    run_suite_cmd.add_argument("--policy", required=True)
    run_suite_cmd.add_argument("--out-dir", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--runs", required=True)

    verify_suite_cmd = sub.add_parser("verify-suite")
    verify_suite_cmd.add_argument("--runs-dir", required=True)

    args = parser.parse_args(argv)

    if args.cmd in {"demo", "run-suite"}:
        inputs = Path(args.inputs if args.cmd == "demo" else args.input_dir)
        policy = Path(args.policy)
        out = Path(args.out if args.cmd == "demo" else args.out_dir)
        for row in run_suite(inputs, out, policy):
            print(
                f"{row['case_id']}: {row['lifecycle_status']} "
                f"effect_created={row['effect_created']} verified={row['verified']}"
            )
        return 0

    if args.cmd in {"verify", "verify-suite"}:
        runs = Path(args.runs if args.cmd == "verify" else args.runs_dir)
        reports = verify_suite(runs)
        failed = [r for r in reports if not r["verified"]]
        for report in reports:
            print(f"{report['case_id']}: verified={report['verified']} errors={len(report['errors'])}")
        return 1 if failed else 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
