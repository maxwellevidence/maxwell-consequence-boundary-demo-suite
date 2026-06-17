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
        "requirements-dev.txt",
        "docs/CLAIMS_AND_LIMITATIONS.md",
        "docs/POLICY_REASON_CODES.md",
        "docs/PUBLIC_SECTOR_DETERMINATION_MODEL.md",
        "policies/public_sector_determination_policy.yml",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel


def test_demo_inputs_are_present() -> None:
    inputs = sorted((ROOT / "examples" / "demo_inputs").glob("*.json"))
    assert len(inputs) == 6
    assert inputs[0].name == "01_complete_eligibility_evidence.json"
