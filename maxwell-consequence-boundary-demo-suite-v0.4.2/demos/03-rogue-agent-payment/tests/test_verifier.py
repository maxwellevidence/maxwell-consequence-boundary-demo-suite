from pathlib import Path

import pytest

from maxwell_rogue_agent_payment.effect_writer import run_all
from maxwell_rogue_agent_payment.verifier import VerificationError, verify_all

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "payment_authority_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_verifier_accepts_fresh_runs(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    reports = verify_all(tmp_path)
    assert len(reports) == 6
    assert any(report["effect_permitted"] for report in reports)
    assert any(not report["effect_permitted"] for report in reports)
    assert any(report["lifecycle_state"] == "PAYMENT_REVIEW_ROUTED" for report in reports)
    assert any(report["lifecycle_state"] == "PAYMENT_EFFECT_SUPPRESSED" for report in reports)


def test_verifier_detects_tampered_manifest_file(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    receipt = tmp_path / "01_low_risk_invoice_valid" / "decision_receipt.json"
    receipt.write_text(
        receipt.read_text(encoding="utf-8").replace("PAYMENT_EFFECT_PERMITTED", "TAMPERED"),
        encoding="utf-8",
    )

    with pytest.raises(VerificationError):
        verify_all(tmp_path)


def test_verifier_rejects_unauthorized_payment_effect_record(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    allowed_effect = tmp_path / "01_low_risk_invoice_valid" / "payment_effect_record.json"
    blocked_effect = tmp_path / "04_self_approval_attempt" / "payment_effect_record.json"
    blocked_effect.write_text(allowed_effect.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(VerificationError):
        verify_all(tmp_path)


def test_verifier_rejects_missing_review_ticket(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    ticket = tmp_path / "02_high_value_missing_dual_approval" / "review_ticket.json"
    ticket.unlink()

    with pytest.raises(VerificationError):
        verify_all(tmp_path)
