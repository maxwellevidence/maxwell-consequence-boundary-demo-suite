from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .effect_writer import run_all, run_case
from .verifier import VerificationError, verify_all


def _print_result_row(result: dict) -> None:
    print(
        f"{result['case_id']}: "
        f"{result['lifecycle_state']} "
        f"({result['reason_code']}) "
        f"payment_effect_permitted={result['effect_permitted']}"
    )


def cmd_demo(args: argparse.Namespace) -> int:
    out = Path(args.out)
    if args.clean and out.exists():
        shutil.rmtree(out)
    results = run_all(Path(args.inputs), Path(args.policy), out)
    print(f"Processed {len(results)} payment demo case(s).")
    for result in results:
        _print_result_row(result)
    print(f"Artifacts written to: {args.out}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    result = run_case(Path(args.input), Path(args.policy), Path(args.out))
    _print_result_row(result)
    print(f"Artifacts written to: {result['run_dir']}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        reports = verify_all(Path(args.runs))
    except VerificationError as exc:
        print(f"VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"Artifact verification passed for {len(reports)} run(s).")
    for report in reports:
        print(
            f"{report['case_id']}: verified "
            f"lifecycle={report['lifecycle_state']} "
            f"payment_effect_permitted={report['effect_permitted']}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maxwell Rogue Agent Payment public demo CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run all payment demo inputs.")
    demo.add_argument("--inputs", default="examples/demo_inputs")
    demo.add_argument("--policy", default="policies/payment_authority_policy.yml")
    demo.add_argument("--out", default="artifacts/runs")
    demo.add_argument("--clean", action="store_true", help="Remove output directory before running.")
    demo.set_defaults(func=cmd_demo)

    run = sub.add_parser("run", help="Run a single payment demo input.")
    run.add_argument("--input", required=True)
    run.add_argument("--policy", default="policies/payment_authority_policy.yml")
    run.add_argument("--out", default="artifacts/runs")
    run.set_defaults(func=cmd_run)

    verify = sub.add_parser("verify", help="Verify generated run artifacts.")
    verify.add_argument("--runs", default="artifacts/runs")
    verify.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
