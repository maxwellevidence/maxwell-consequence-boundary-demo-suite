from __future__ import annotations

import json
from pathlib import Path

from maxwell_human_review_escalation.engine import load_policy, run_suite, verify_run, verify_suite

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "demo_inputs"
POLICY = ROOT / "policies" / "review_escalation_policy.yml"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_expected_lifecycle_and_reason_codes(tmp_path: Path) -> None:
    results = run_suite(INPUTS, tmp_path / "runs", POLICY)
    by_case = {row["case_id"]: row for row in results}
    expected = {
        "01_hold_missing_evidence": ("review_routed", "REVIEW_REQUIRED_MISSING_EVIDENCE", False),
        "02_reviewer_adds_evidence": ("review_approved_effect_committed", "REVIEW_APPROVED_EFFECT_COMMITTED", True),
        "03_reviewer_lacks_authority": ("review_rejected_effect_suppressed", "REVIEWER_LACKS_AUTHORITY", False),
        "04_authorized_reviewer_approves": ("review_approved_effect_committed", "REVIEW_APPROVED_EFFECT_COMMITTED", True),
        "05_review_fails_blocked": ("effect_suppressed", "PROMPT_INJECTION_NOT_AUTHORITY", False),
        "06_review_attempts_scope_expansion": ("review_rejected_effect_suppressed", "REVIEW_SCOPE_EXPANSION_BLOCKED", False),
    }
    assert set(by_case) == set(expected)
    for case_id, (lifecycle, reason, effect_created) in expected.items():
        assert by_case[case_id]["lifecycle_status"] == lifecycle
        assert by_case[case_id]["reason_code"] == reason
        assert by_case[case_id]["effect_created"] is effect_created
        assert by_case[case_id]["verified"] is True


def test_no_authorized_effect_for_pending_or_rejected_review(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    for run_dir in sorted((tmp_path / "runs").iterdir()):
        receipt = read_json(run_dir / "decision_receipt.json")
        effect_exists = (run_dir / "authorized_effect_record.json").exists()
        if receipt["effect_permitted"]:
            assert effect_exists
            assert not (run_dir / "NO_AUTHORIZED_EFFECT_CREATED.txt").exists()
        else:
            assert not effect_exists
            assert (run_dir / "NO_AUTHORIZED_EFFECT_CREATED.txt").exists()


def test_reviewer_adds_evidence_and_creates_effect(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "02_reviewer_adds_evidence"
    review_event = read_json(run_dir / "review_event.json")
    receipt = read_json(run_dir / "decision_receipt.json")
    assert "risk_assessment" in review_event["added_evidence_refs"]
    assert receipt["effect_permitted"] is True
    assert (run_dir / "authorized_effect_record.json").exists()


def test_reviewer_lacks_authority_cannot_create_effect(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "03_reviewer_lacks_authority"
    review_auth = read_json(run_dir / "review_authority_context.json")
    receipt = read_json(run_dir / "decision_receipt.json")
    assert review_auth["can_review"] is False
    assert receipt["reason_code"] == "REVIEWER_LACKS_AUTHORITY"
    assert not (run_dir / "authorized_effect_record.json").exists()
    assert (run_dir / "review_rejection_notice.json").exists()


def test_prompt_injection_is_not_review_authority(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "05_review_fails_blocked"
    evidence = read_json(run_dir / "initial_evidence_bundle.json")
    receipt = read_json(run_dir / "decision_receipt.json")
    assert evidence["prompt_injection_detected"] is True
    assert receipt["reason_code"] == "PROMPT_INJECTION_NOT_AUTHORITY"
    assert not (run_dir / "authorized_effect_record.json").exists()


def test_review_scope_expansion_is_blocked(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "06_review_attempts_scope_expansion"
    review_event = read_json(run_dir / "review_event.json")
    receipt = read_json(run_dir / "decision_receipt.json")
    assert review_event["review_effect_type"] != read_json(run_dir / "input_request.json")["proposed_action"]["effect_type"]
    assert receipt["reason_code"] == "REVIEW_SCOPE_EXPANSION_BLOCKED"
    assert receipt["effect_permitted"] is False


def test_verifier_detects_tampered_receipt(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "02_reviewer_adds_evidence"
    receipt_path = run_dir / "decision_receipt.json"
    receipt = read_json(receipt_path)
    receipt["reason_code"] = "TAMPERED"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = verify_run(run_dir, write_report=False)
    assert report["verified"] is False
    assert report["tamper_detected"] is True
    assert any("hash mismatch" in err for err in report["errors"])


def test_verifier_rejects_fake_effect_for_rejected_review(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "03_reviewer_lacks_authority"
    (run_dir / "authorized_effect_record.json").write_text('{"record_type":"fake_effect"}\n', encoding="utf-8")
    report = verify_run(run_dir, write_report=False)
    assert report["verified"] is False
    assert any("exists despite effect_permitted=false" in err for err in report["errors"])


def test_policy_contains_public_preview_reason_codes() -> None:
    policy = load_policy(POLICY)
    codes = set(policy["reason_codes"].values())
    assert "REVIEW_APPROVED_EFFECT_COMMITTED" in codes
    assert "REVIEWER_LACKS_AUTHORITY" in codes
    assert "REVIEW_SCOPE_EXPANSION_BLOCKED" in codes


def test_verify_suite_reports_all_runs_verified(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    reports = verify_suite(tmp_path / "runs")
    assert len(reports) == 6
    assert all(report["verified"] for report in reports)
