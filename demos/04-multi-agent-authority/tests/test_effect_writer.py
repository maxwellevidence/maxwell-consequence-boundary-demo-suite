from pathlib import Path

from maxwell_multi_agent_authority.effect_writer import run_case
from maxwell_multi_agent_authority.paths import read_json, sha256_json

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "multi_agent_authority_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_permitted_case_creates_delegated_effect_record(tmp_path):
    result = run_case(INPUTS / "01_valid_delegated_handoff.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    assert (run_dir / "delegated_effect_record.json").exists()
    assert not (run_dir / "NO_DELEGATED_EFFECT_CREATED.txt").exists()
    assert not (run_dir / "review_ticket.json").exists()
    assert not (run_dir / "suppression_notice.json").exists()

    receipt = read_json(run_dir / "decision_receipt.json")
    effect = read_json(run_dir / "delegated_effect_record.json")
    assert receipt["effect_permitted"] is True
    assert effect["decision_receipt_sha256"] == sha256_json(receipt)
    assert effect["synthetic_no_real_downstream_action"] is True


def test_review_routed_case_creates_review_ticket_no_effect(tmp_path):
    result = run_case(INPUTS / "05_handoff_loses_evidence_packet.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    assert not (run_dir / "delegated_effect_record.json").exists()
    assert (run_dir / "NO_DELEGATED_EFFECT_CREATED.txt").exists()
    assert (run_dir / "review_ticket.json").exists()
    assert not (run_dir / "suppression_notice.json").exists()

    receipt = read_json(run_dir / "decision_receipt.json")
    ticket = read_json(run_dir / "review_ticket.json")
    assert receipt["lifecycle_state"] == "DELEGATION_REVIEW_ROUTED"
    assert ticket["decision_receipt_sha256"] == sha256_json(receipt)


def test_suppressed_case_creates_suppression_notice_no_effect(tmp_path):
    result = run_case(INPUTS / "03_agent_expands_task_beyond_scope.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    assert not (run_dir / "delegated_effect_record.json").exists()
    assert (run_dir / "NO_DELEGATED_EFFECT_CREATED.txt").exists()
    assert not (run_dir / "review_ticket.json").exists()
    assert (run_dir / "suppression_notice.json").exists()

    receipt = read_json(run_dir / "decision_receipt.json")
    notice = read_json(run_dir / "suppression_notice.json")
    assert receipt["lifecycle_state"] == "DELEGATED_EFFECT_SUPPRESSED"
    assert notice["decision_receipt_sha256"] == sha256_json(receipt)
