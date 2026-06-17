from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_files_exist():
    for rel in [
        "README.md",
        "REVIEWER_START_HERE.md",
        "DEMO_SPEC.yml",
        "LICENSE",
        "SECURITY.md",
        "Makefile",
        "pyproject.toml",
        "docs/CLAIMS_AND_LIMITATIONS.md",
        "docs/RECONSTRUCTION_MODEL.md",
        "docs/TAMPER_DETECTION_NOTE.md",
    ]:
        assert (ROOT / rel).exists(), rel


def test_no_private_env_file_checked_in():
    assert not (ROOT / ".env").exists()
