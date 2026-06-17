"""Export reviewed sample artifacts for the public Maxwell Effect Gate proof.

This helper regenerates the demo artifacts and copies them into artifacts/sample_outputs/
so reviewers can inspect expected outputs without running the demo first.
"""

import shutil

from maxwell_effect_gate.run_demo import ARTIFACTS_DIR, VALID_CASES, main as run_demo_main
from maxwell_effect_gate.verify_artifacts import main as verify_artifacts_main


SAMPLE_ARTIFACTS_DIR = ARTIFACTS_DIR / "sample_outputs"


def export_sample_artifacts() -> None:
    """Regenerate, verify, and export sample artifacts."""

    run_demo_main([])
    verify_artifacts_main()

    artifacts_readme = ARTIFACTS_DIR / "README.md"
    artifacts_readme.write_text(
        "# Artifacts\n\n"
        "`make demo` creates generated run folders directly under this directory.\n\n"
        "Reviewed sample outputs are exported to `artifacts/sample_outputs/`.\n\n"
        "Generated run folders are excluded from clean release packages unless "
        "intentionally copied into `artifacts/sample_outputs/`.\n",
        encoding="utf-8",
    )

    if SAMPLE_ARTIFACTS_DIR.exists():
        shutil.rmtree(SAMPLE_ARTIFACTS_DIR)

    SAMPLE_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    for case in VALID_CASES:
        run_name = f"{case}_run"
        source_dir = ARTIFACTS_DIR / run_name
        target_dir = SAMPLE_ARTIFACTS_DIR / run_name
        shutil.copytree(source_dir, target_dir)

    readme = SAMPLE_ARTIFACTS_DIR / "README.md"
    readme.write_text(
        "# Sample Artifacts\n\n"
        "This folder contains reviewed sample outputs from the Maxwell Effect Gate public proof.\n\n"
        "The run folder names describe input shape, not expected outcome. Inspect "
        "each decision_receipt.json for the derived decision and matched policy rule.\n\n"
        "The samples are public-safe. They do not disclose Maxwell's private authority model, "
        "evaluator chains, scoring rules, thresholds, internal authority logic, "
        "internal evidence machinery, or production enforcement logic.\n\n"
        "## Core invariant\n\n"
        "```text\n"
        "Only a policy-derived allow creates effect_record.json.\n"
        "pause and block do not create effect_record.json.\n"
        "Every run emits a repo-anchored signed manifest over generated JSON/YAML artifacts.\n"
        "```\n",
        encoding="utf-8",
    )

    print("Exported reviewed sample artifacts to artifacts/sample_outputs/.")


def main() -> None:
    """CLI entry point."""

    export_sample_artifacts()


if __name__ == "__main__":
    main()
