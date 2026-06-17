from __future__ import annotations

import argparse
from pathlib import Path

from .engine import reconstruct_suite, run_suite, tamper_lab, verify_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Maxwell Incident Reconstruction Demo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    demo = sub.add_parser("demo")
    demo.add_argument("--inputs", required=True)
    demo.add_argument("--policy", required=True)
    demo.add_argument("--out", required=True)

    run_suite_cmd = sub.add_parser("run-suite")
    run_suite_cmd.add_argument("--input-dir", required=True)
    run_suite_cmd.add_argument("--out-dir", required=True)
    run_suite_cmd.add_argument("--policy", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--runs", required=True)

    verify_suite_cmd = sub.add_parser("verify-suite")
    verify_suite_cmd.add_argument("--runs-dir", required=True)

    reconstruct = sub.add_parser("reconstruct")
    reconstruct.add_argument("--runs", required=True)
    reconstruct.add_argument("--out", required=True)

    reconstruct_suite_cmd = sub.add_parser("reconstruct-suite")
    reconstruct_suite_cmd.add_argument("--runs-dir", required=True)
    reconstruct_suite_cmd.add_argument("--out-dir", default=None)

    tamper = sub.add_parser("tamper-demo")
    tamper.add_argument("--runs", required=True)
    tamper.add_argument("--out", required=True)

    tamper_lab_cmd = sub.add_parser("tamper-lab")
    tamper_lab_cmd.add_argument("--runs-dir", required=True)
    tamper_lab_cmd.add_argument("--out-dir", required=True)

    args = parser.parse_args(argv)

    if args.cmd in {"demo", "run-suite"}:
        inputs = Path(args.inputs if args.cmd == "demo" else args.input_dir)
        out = Path(args.out if args.cmd == "demo" else args.out_dir)
        policy = Path(args.policy)
        for row in run_suite(inputs, out, policy):
            print(f"{row['case_id']}: {row['lifecycle_status']} effect_created={row['effect_created']} verified={row['verified']}")
        return 0

    if args.cmd in {"verify", "verify-suite"}:
        runs = Path(args.runs if args.cmd == "verify" else args.runs_dir)
        reports = verify_suite(runs)
        for report in reports:
            print(f"{report['case_id']}: {'verified' if report['verified'] else 'FAILED'}")
        return 0 if all(report["verified"] for report in reports) else 1

    if args.cmd in {"reconstruct", "reconstruct-suite"}:
        runs = Path(args.runs if args.cmd == "reconstruct" else args.runs_dir)
        if args.cmd == "reconstruct":
            out = Path(args.out)
        else:
            out = Path(args.out_dir) if args.out_dir else runs.parent / "reconstruction"
        for report in reconstruct_suite(runs, out):
            print(f"{report['case_id']}: {report['decision_summary']['lifecycle_status']} effect_record_exists={report['effect_status']['effect_record_exists']}")
        return 0

    if args.cmd in {"tamper-demo", "tamper-lab"}:
        runs = Path(args.runs if args.cmd == "tamper-demo" else args.runs_dir)
        out = Path(args.out if args.cmd == "tamper-demo" else args.out_dir)
        result = tamper_lab(runs, out)
        print(f"tamper_demo: tamper_detected={result['tamper_detected']} verified={result['verified']}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
