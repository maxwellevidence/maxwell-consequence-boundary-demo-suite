from pathlib import Path

from maxwell_incident_reconstruction.engine import evaluate, load_policy, read_json, reconstruct, run_suite, tamper_lab

ROOT = Path(__file__).resolve().parents[1]
POLICY = load_policy(ROOT / "policies/incident_reconstruction_policy.yml")


def case(name: str):
    return read_json(ROOT / "examples/demo_inputs" / f"{name}.json")


def test_policy_outcomes():
    assert evaluate(case("01_permitted_action_effect_committed"), POLICY)["reason_code"] == "IR_POLICY_ALLOW"
    assert evaluate(case("02_reviewed_action_needs_human"), POLICY)["reason_code"] == "IR_REVIEW_HIGH_RISK"
    assert evaluate(case("03_blocked_scope_violation"), POLICY)["reason_code"] == "IR_BLOCK_SCOPE_VIOLATION"
    assert evaluate(case("04_attempted_action_missing_authority"), POLICY)["reason_code"] == "IR_BLOCK_MISSING_AUTHORITY"
    assert evaluate(case("06_stale_policy_context_requires_review"), POLICY)["reason_code"] == "IR_REVIEW_STALE_POLICY_CONTEXT"


def test_only_permitted_cases_create_effect_record(tmp_path):
    run_suite(ROOT / "examples/demo_inputs", tmp_path, ROOT / "policies/incident_reconstruction_policy.yml")
    allowed = {"01_permitted_action_effect_committed", "05_tamper_detection_lab_seed"}
    for run_dir in [p for p in tmp_path.iterdir() if p.is_dir()]:
        assert (run_dir / "effect_record.json").exists() == (run_dir.name in allowed)
        assert (run_dir / "NO_EFFECT_CREATED.txt").exists() == (run_dir.name not in allowed)


def test_reconstruction_exists_for_no_effect(tmp_path):
    run_suite(ROOT / "examples/demo_inputs", tmp_path, ROOT / "policies/incident_reconstruction_policy.yml")
    report = reconstruct(tmp_path / "04_attempted_action_missing_authority")
    assert report["effect_status"]["effect_record_exists"] is False
    assert report["authority_summary"]["authority_present"] is False


def test_tamper_detected(tmp_path):
    runs = tmp_path / "runs"
    lab = tmp_path / "lab"
    run_suite(ROOT / "examples/demo_inputs", runs, ROOT / "policies/incident_reconstruction_policy.yml")
    result = tamper_lab(runs, lab)
    assert result["tamper_detected"] is True
    assert result["verified"] is False
