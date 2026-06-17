from __future__ import annotations

import json
from pathlib import Path

from maxwell_sensitive_data_access.engine import load_policy, run_suite, verify_run, verify_suite

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "demo_inputs"
POLICY = ROOT / "policies" / "data_access_policy.yml"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_expected_lifecycle_and_reason_codes(tmp_path: Path) -> None:
    results = run_suite(INPUTS, tmp_path / "runs", POLICY)
    by_case = {row["case_id"]: row for row in results}
    expected = {
        "01_valid_role_and_purpose": ("access_effect_committed", "DATA_ACCESS_EFFECT_COMMITTED", True),
        "02_missing_business_purpose": ("review_routed", "DATA_PURPOSE_MISSING", False),
        "03_restricted_data_class": ("access_suppressed", "DATA_CLASSIFICATION_EXCEEDS_CLEARANCE", False),
        "04_outside_scope_employee_record": ("access_suppressed", "DATASET_SCOPE_VIOLATION", False),
        "05_prompt_injection_restricted_data": ("access_suppressed", "PROMPT_INJECTION_NOT_AUTHORITY", False),
        "06_excessive_data_minimization_failure": ("review_routed", "DATA_MINIMIZATION_REVIEW_REQUIRED", False),
    }
    assert set(by_case) == set(expected)
    for case_id, (lifecycle, reason, effect_created) in expected.items():
        assert by_case[case_id]["lifecycle_status"] == lifecycle
        assert by_case[case_id]["reason_code"] == reason
        assert by_case[case_id]["effect_created"] is effect_created
        assert by_case[case_id]["verified"] is True


def test_no_data_access_effect_for_review_or_suppressed_cases(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    for run_dir in sorted((tmp_path / "runs").iterdir()):
        receipt = read_json(run_dir / "decision_receipt.json")
        effect_exists = (run_dir / "data_access_effect_record.json").exists()
        if receipt["effect_permitted"]:
            assert effect_exists
            assert not (run_dir / "NO_DATA_ACCESS_EFFECT_CREATED.txt").exists()
        else:
            assert not effect_exists
            assert (run_dir / "NO_DATA_ACCESS_EFFECT_CREATED.txt").exists()


def test_prompt_injection_is_preserved_but_not_authority(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "05_prompt_injection_restricted_data"
    evidence = read_json(run_dir / "data_evidence_bundle.json")
    receipt = read_json(run_dir / "decision_receipt.json")
    assert evidence["prompt_injection_detected"] is True
    assert receipt["reason_code"] == "PROMPT_INJECTION_NOT_AUTHORITY"
    assert receipt["effect_permitted"] is False
    assert not (run_dir / "data_access_effect_record.json").exists()


def test_verifier_detects_tampered_receipt(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "01_valid_role_and_purpose"
    receipt_path = run_dir / "decision_receipt.json"
    receipt = read_json(receipt_path)
    receipt["reason_code"] = "TAMPERED"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = verify_run(run_dir, write_report=False)
    assert report["verified"] is False
    assert report["tamper_detected"] is True
    assert any("hash mismatch" in err for err in report["errors"])


def test_verifier_rejects_fake_effect_record_for_suppressed_case(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    run_dir = tmp_path / "runs" / "04_outside_scope_employee_record"
    (run_dir / "data_access_effect_record.json").write_text(
        '{"record_type":"fake_data_access_effect_record"}\n', encoding="utf-8"
    )
    report = verify_run(run_dir, write_report=False)
    assert report["verified"] is False
    assert any("exists despite effect_permitted=false" in err for err in report["errors"])


def test_policy_contains_public_preview_reason_codes() -> None:
    policy = load_policy(POLICY)
    codes = set(policy["reason_codes"].values())
    assert "DATA_ACCESS_EFFECT_COMMITTED" in codes
    assert "PROMPT_INJECTION_NOT_AUTHORITY" in codes
    assert "DATA_MINIMIZATION_REVIEW_REQUIRED" in codes


def test_verify_suite_reports_all_runs_verified(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path / "runs", POLICY)
    reports = verify_suite(tmp_path / "runs")
    assert len(reports) == 6
    assert all(report["verified"] for report in reports)
