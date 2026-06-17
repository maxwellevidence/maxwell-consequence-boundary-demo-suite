from pathlib import Path

import pytest

from maxwell_effect_gate_basic.effect_writer import run_all
from maxwell_effect_gate_basic.verifier import VerificationError, verify_all

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "effect_gate_basic_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_verifier_accepts_fresh_runs(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    reports = verify_all(tmp_path)
    assert len(reports) == 6
    assert any(report["effect_permitted"] for report in reports)
    assert any(not report["effect_permitted"] for report in reports)


def test_verifier_detects_tampered_manifest_file(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    receipt = tmp_path / "01_valid_low_risk_notice" / "decision_receipt.json"
    receipt.write_text(
        receipt.read_text(encoding="utf-8").replace("EFFECT_GATE_EFFECT_PERMITTED", "TAMPERED"),
        encoding="utf-8",
    )

    with pytest.raises(VerificationError):
        verify_all(tmp_path)


def test_verifier_rejects_unauthorized_effect_record(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    allowed_effect = tmp_path / "01_valid_low_risk_notice" / "effect_record.json"
    blocked_effect = tmp_path / "04_scope_violation_suppressed" / "effect_record.json"
    blocked_effect.write_text(allowed_effect.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(VerificationError):
        verify_all(tmp_path)
