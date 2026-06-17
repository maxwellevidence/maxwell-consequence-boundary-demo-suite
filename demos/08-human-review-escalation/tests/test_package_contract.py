from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_public_files_exist() -> None:
    required = [
        "README.md",
        "REVIEWER_START_HERE.md",
        "DEMO_BUILD_BRIEF.md",
        "DEMO_SPEC.yml",
        "LICENSE",
        "LICENSE-NOTICE.md",
        "SECURITY.md",
        "NOTICE.md",
        "VERSION",
        "Makefile",
        "pyproject.toml",
        "docs/CLAIMS_AND_LIMITATIONS.md",
        "docs/DEMO_WALKTHROUGH.md",
        "docs/POLICY_REASON_CODES.md",
        "docs/HUMAN_REVIEW_ESCALATION_MODEL.md",
        "tools/public_package_check.py",
        "tools/create_clean_zip.py",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel


def test_version_file_matches_package_version() -> None:
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.1.0"


def test_no_accidental_generated_run_artifacts_are_checked_in() -> None:
    assert not (ROOT / "artifacts" / "runs").exists()
