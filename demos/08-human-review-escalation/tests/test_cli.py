from __future__ import annotations

from pathlib import Path

from maxwell_human_review_escalation.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_demo_and_verify(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    assert main([
        "demo",
        "--inputs",
        str(ROOT / "examples" / "demo_inputs"),
        "--policy",
        str(ROOT / "policies" / "review_escalation_policy.yml"),
        "--out",
        str(out),
    ]) == 0
    assert main(["verify", "--runs", str(out)]) == 0
    assert (out / "02_reviewer_adds_evidence" / "authorized_effect_record.json").exists()
    assert not (out / "03_reviewer_lacks_authority" / "authorized_effect_record.json").exists()
