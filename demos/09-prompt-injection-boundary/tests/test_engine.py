from __future__ import annotations

from pathlib import Path

from maxwell_prompt_injection_boundary.engine import (
    EFFECT_FILE,
    NO_EFFECT_FILE,
    load_policy,
    read_json,
    run_case,
    run_suite,
    verify_run,
    verify_suite,
)

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "demo_inputs"
POLICY = ROOT / "policies" / "prompt_injection_boundary_policy.yml"


def run_named(tmp_path: Path, name: str) -> Path:
    policy = load_policy(POLICY)
    run_case(INPUTS / f"{name}.json", tmp_path, policy)
    return tmp_path / name


def receipt(run_dir: Path) -> dict:
    return read_json(run_dir / "decision_receipt.json")


def test_run_suite_all_cases_verify(tmp_path: Path) -> None:
    rows = run_suite(INPUTS, tmp_path, POLICY)
    assert len(rows) == 6
    assert all(row["verified"] for row in rows)
    reports = verify_suite(tmp_path)
    assert len(reports) == 6
    assert all(report["verified"] for report in reports)


def test_clean_case_creates_bounded_effect(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "01_normal_instruction_valid")
    rec = receipt(run_dir)
    assert rec["effect_permitted"] is True
    assert rec["reason_code"] == "PROMPT_BOUNDARY_EFFECT_COMMITTED"
    assert (run_dir / EFFECT_FILE).exists()
    assert not (run_dir / NO_EFFECT_FILE).exists()


def test_ignore_policy_instruction_is_quarantined(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "02_ignore_policy_instruction")
    rec = receipt(run_dir)
    boundary = read_json(run_dir / "prompt_boundary_analysis.json")
    assert rec["effect_permitted"] is False
    assert rec["quarantine_required"] is True
    assert boundary["prompt_injection_detected"] is True
    assert (run_dir / "quarantine_ticket.json").exists()
    assert (run_dir / NO_EFFECT_FILE).exists()
    assert not (run_dir / EFFECT_FILE).exists()


def test_urgent_override_attempt_is_quarantined(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "03_urgent_override_attempt")
    rec = receipt(run_dir)
    assert rec["reason_code"] == "PROMPT_INJECTION_BOUNDARY_TRIGGERED"
    assert rec["effect_permitted"] is False
    assert (run_dir / "quarantine_ticket.json").exists()


def test_fake_manager_approval_is_untrusted_authority(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "04_fake_manager_approval")
    rec = receipt(run_dir)
    boundary = read_json(run_dir / "prompt_boundary_analysis.json")
    assert rec["reason_code"] == "UNTRUSTED_AUTHORITY_CLAIM"
    assert boundary["untrusted_authority_claim_present"] is True
    assert not (run_dir / EFFECT_FILE).exists()


def test_malicious_tool_request_is_suppressed(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "05_malicious_tool_request")
    rec = receipt(run_dir)
    boundary = read_json(run_dir / "prompt_boundary_analysis.json")
    assert rec["effect_permitted"] is False
    assert rec["reason_code"] in {"TOOL_REQUEST_OUTSIDE_BOUNDARY", "PROMPT_INJECTION_BOUNDARY_TRIGGERED"}
    assert boundary["tool_prohibited"] is True
    assert not (run_dir / EFFECT_FILE).exists()


def test_risk_downgrade_routes_to_security_review(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "06_model_relabels_high_risk_low")
    rec = receipt(run_dir)
    boundary = read_json(run_dir / "prompt_boundary_analysis.json")
    assert rec["effect_permitted"] is False
    assert rec["security_review_required"] is True
    assert rec["reason_code"] == "MODEL_RISK_DOWNGRADE_REQUIRES_SECURITY_REVIEW"
    assert boundary["risk_downgrade_attempt_detected"] is True
    assert (run_dir / "security_review_ticket.json").exists()


def test_non_permitted_cases_never_create_effect(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path, POLICY)
    for run_dir in tmp_path.iterdir():
        rec = receipt(run_dir)
        if not rec["effect_permitted"]:
            assert not (run_dir / EFFECT_FILE).exists()
            assert (run_dir / NO_EFFECT_FILE).exists()


def test_tamper_detection(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "01_normal_instruction_valid")
    effect_path = run_dir / EFFECT_FILE
    data = read_json(effect_path)
    data["effect_payload"] = {"tampered": True}
    effect_path.write_text(__import__("json").dumps(data, indent=2) + "\n", encoding="utf-8")
    report = verify_run(run_dir)
    assert report["verified"] is False
    assert report["tamper_detected"] is True
    assert any("hash mismatch" in err for err in report["errors"])


def test_verifier_rejects_missing_effect_for_permitted_case(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "01_normal_instruction_valid")
    (run_dir / EFFECT_FILE).unlink()
    report = verify_run(run_dir)
    assert report["verified"] is False
    assert any(EFFECT_FILE in err for err in report["errors"])


def test_manifest_exists_for_each_run(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path, POLICY)
    for run_dir in tmp_path.iterdir():
        assert (run_dir / "manifest.json").exists()
        assert (run_dir / "verification_report.json").exists()
