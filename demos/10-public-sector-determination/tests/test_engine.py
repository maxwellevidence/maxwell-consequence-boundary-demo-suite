from __future__ import annotations

from pathlib import Path

from maxwell_public_sector_determination.engine import (
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
POLICY = ROOT / "policies" / "public_sector_determination_policy.yml"


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


def test_complete_eligibility_evidence_creates_effect(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "01_complete_eligibility_evidence")
    rec = receipt(run_dir)
    assert rec["effect_permitted"] is True
    assert rec["reason_code"] == "PUBLIC_SECTOR_DETERMINATION_EFFECT_COMMITTED"
    assert (run_dir / EFFECT_FILE).exists()
    assert not (run_dir / NO_EFFECT_FILE).exists()


def test_missing_required_document_routes_review_without_effect(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "02_missing_required_document")
    rec = receipt(run_dir)
    ev = read_json(run_dir / "determination_evidence_bundle.json")
    assert rec["effect_permitted"] is False
    assert rec["case_review_required"] is True
    assert rec["reason_code"] == "REQUIRED_ELIGIBILITY_EVIDENCE_MISSING"
    assert "income_verified" in ev["missing_refs"]
    assert (run_dir / "case_review_ticket.json").exists()
    assert not (run_dir / EFFECT_FILE).exists()


def test_inconsistent_case_record_routes_review(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "03_inconsistent_case_record")
    rec = receipt(run_dir)
    ev = read_json(run_dir / "determination_evidence_bundle.json")
    assert ev["case_record_consistent"] is False
    assert rec["reason_code"] == "CASE_RECORD_INCONSISTENT_REQUIRES_REVIEW"
    assert rec["effect_permitted"] is False
    assert (run_dir / "case_review_ticket.json").exists()


def test_unauthorized_auto_denial_suppressed(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "04_unauthorized_auto_denial")
    rec = receipt(run_dir)
    due = read_json(run_dir / "due_process_analysis.json")
    assert rec["effect_permitted"] is False
    assert rec["reason_code"] == "UNAUTHORIZED_AUTOMATED_ADVERSE_DETERMINATION"
    assert due["ai_claims_final_authority"] is True
    assert due["ai_output_treated_as_authority"] is False
    assert (run_dir / "suppression_notice.json").exists()
    assert not (run_dir / EFFECT_FILE).exists()


def test_review_required_due_process_creates_due_process_ticket(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "05_review_required_due_process")
    rec = receipt(run_dir)
    due = read_json(run_dir / "due_process_analysis.json")
    assert rec["effect_permitted"] is False
    assert rec["due_process_review_required"] is True
    assert rec["reason_code"] == "DUE_PROCESS_REVIEW_REQUIRED"
    assert due["adverse_determination"] is True
    assert (run_dir / "due_process_review_ticket.json").exists()


def test_authorized_reviewed_determination_creates_effect(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "06_authorized_reviewed_determination_effect")
    rec = receipt(run_dir)
    review_auth = read_json(run_dir / "review_authority_context.json")
    effect = read_json(run_dir / EFFECT_FILE)
    assert rec["effect_permitted"] is True
    assert rec["reason_code"] == "PUBLIC_SECTOR_DETERMINATION_EFFECT_COMMITTED"
    assert review_auth["review_authority_present"] is True
    assert effect["adverse"] is True
    assert not (run_dir / NO_EFFECT_FILE).exists()


def test_non_permitted_cases_never_create_effect(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path, POLICY)
    for run_dir in tmp_path.iterdir():
        rec = receipt(run_dir)
        if not rec["effect_permitted"]:
            assert not (run_dir / EFFECT_FILE).exists()
            assert (run_dir / NO_EFFECT_FILE).exists()


def test_tamper_detection(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "01_complete_eligibility_evidence")
    effect_path = run_dir / EFFECT_FILE
    data = read_json(effect_path)
    data["determination_effect"] = "tampered_effect"
    effect_path.write_text(__import__("json").dumps(data, indent=2) + "\n", encoding="utf-8")
    report = verify_run(run_dir)
    assert report["verified"] is False
    assert report["tamper_detected"] is True
    assert any("hash mismatch" in err for err in report["errors"])


def test_verifier_rejects_missing_effect_for_permitted_case(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "01_complete_eligibility_evidence")
    (run_dir / EFFECT_FILE).unlink()
    report = verify_run(run_dir)
    assert report["verified"] is False
    assert any(EFFECT_FILE in err for err in report["errors"])


def test_verifier_rejects_fake_effect_for_non_permitted_case(tmp_path: Path) -> None:
    run_dir = run_named(tmp_path, "02_missing_required_document")
    (run_dir / EFFECT_FILE).write_text("{}\n", encoding="utf-8")
    report = verify_run(run_dir)
    assert report["verified"] is False
    assert any("exists despite effect_permitted=false" in err for err in report["errors"])


def test_manifest_exists_for_each_run(tmp_path: Path) -> None:
    run_suite(INPUTS, tmp_path, POLICY)
    for run_dir in tmp_path.iterdir():
        assert (run_dir / "manifest.json").exists()
        assert (run_dir / "verification_report.json").exists()
