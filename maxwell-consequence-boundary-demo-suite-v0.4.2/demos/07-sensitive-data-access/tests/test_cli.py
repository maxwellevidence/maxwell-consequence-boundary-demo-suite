from __future__ import annotations

from pathlib import Path

from maxwell_sensitive_data_access.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_demo_and_verify(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    assert main([
        "demo",
        "--inputs",
        str(ROOT / "examples" / "demo_inputs"),
        "--policy",
        str(ROOT / "policies" / "data_access_policy.yml"),
        "--out",
        str(out),
    ]) == 0
    assert main(["verify", "--runs", str(out)]) == 0
    assert (out / "01_valid_role_and_purpose" / "data_access_effect_record.json").exists()
    assert not (out / "05_prompt_injection_restricted_data" / "data_access_effect_record.json").exists()
