from pathlib import Path

import pytest

from maxwell_multi_agent_authority.effect_writer import run_all
from maxwell_multi_agent_authority.verifier import VerificationError, verify_all

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "multi_agent_authority_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_verifier_accepts_fresh_runs(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    reports = verify_all(tmp_path)
    assert len(reports) == 6
    assert any(report["effect_permitted"] for report in reports)
    assert any(not report["effect_permitted"] for report in reports)
    assert any(report["lifecycle_state"] == "DELEGATION_REVIEW_ROUTED" for report in reports)
    assert any(report["lifecycle_state"] == "DELEGATED_EFFECT_SUPPRESSED" for report in reports)


def test_verifier_detects_tampered_manifest_file(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    receipt = tmp_path / "01_valid_delegated_handoff" / "decision_receipt.json"
    receipt.write_text(
        receipt.read_text(encoding="utf-8").replace("DELEGATED_EFFECT_PERMITTED", "TAMPERED"),
        encoding="utf-8",
    )

    with pytest.raises(VerificationError):
        verify_all(tmp_path)


def test_verifier_rejects_unauthorized_delegated_effect_record(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    allowed_effect = tmp_path / "01_valid_delegated_handoff" / "delegated_effect_record.json"
    blocked_effect = tmp_path / "03_agent_expands_task_beyond_scope" / "delegated_effect_record.json"
    blocked_effect.write_text(allowed_effect.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(VerificationError):
        verify_all(tmp_path)


def test_verifier_rejects_missing_review_ticket(tmp_path):
    run_all(INPUTS, POLICY, tmp_path)
    ticket = tmp_path / "02_handoff_missing_authority_scope" / "review_ticket.json"
    ticket.unlink()

    with pytest.raises(VerificationError):
        verify_all(tmp_path)
