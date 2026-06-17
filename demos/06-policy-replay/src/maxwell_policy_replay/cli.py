from __future__ import annotations

import argparse
from pathlib import Path

from .engine import replay_suite, run_suite, verify_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Maxwell Policy Replay Demo")
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

    replay = sub.add_parser("replay")
    replay.add_argument("--runs", required=True)
    replay.add_argument("--target-policy", required=True)
    replay.add_argument("--out", required=True)

    replay_suite_cmd = sub.add_parser("replay-suite")
    replay_suite_cmd.add_argument("--runs-dir", required=True)
    replay_suite_cmd.add_argument("--target-policy", required=True)
    replay_suite_cmd.add_argument("--out-dir", required=True)

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
        for report in reports:
            print(f"{report['case_id']}: {'verified' if report['verified'] else 'FAILED'}")
        return 0 if all(report["verified"] for report in reports) else 1

    if args.cmd in {"replay", "replay-suite"}:
        runs = Path(args.runs if args.cmd == "replay" else args.runs_dir)
        policy = Path(args.target_policy)
        out = Path(args.out if args.cmd == "replay" else args.out_dir)
        reports = replay_suite(runs, policy, out)
        for report in reports:
            print(
                f"{report['case_id']}: {report['drift_class']} "
                f"changed={report['outcome_changed']} mutated={report['effect_record_mutated']}"
            )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
