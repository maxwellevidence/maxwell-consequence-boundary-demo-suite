from pathlib import Path

from maxwell_policy_replay.engine import evaluate, load_policy, read_json, replay_suite, run_suite, verify_run

ROOT = Path(__file__).resolve().parents[1]
POLICY_V1 = load_policy(ROOT / "policies/policy_v1.yml")
POLICY_V2 = load_policy(ROOT / "policies/policy_v2.yml")


def case(name: str):
    return read_json(ROOT / "examples/demo_inputs" / f"{name}.json")


def test_original_policy_outcomes():
    assert evaluate(case("01_allowed_under_policy_v1"), POLICY_V1)["decision"] == "allow"
    assert evaluate(case("02_same_evidence_policy_v2_requires_review"), POLICY_V1)["decision"] == "allow"
    assert evaluate(case("03_threshold_changed"), POLICY_V1)["decision"] == "allow"
    assert evaluate(case("04_authority_rule_changed"), POLICY_V1)["decision"] == "allow"
    assert evaluate(case("05_blocked_under_both_scope_violation"), POLICY_V1)["reason_code"] == "PR_BLOCK_SCOPE_VIOLATION"
    assert evaluate(case("06_current_policy_would_allow_but_no_retroactive_effect"), POLICY_V1)["reason_code"] == "PR_BLOCK_EFFECT_NOT_IN_ROLE_SCOPE"


def test_target_policy_outcomes_show_drift():
    assert evaluate(case("01_allowed_under_policy_v1"), POLICY_V2)["decision"] == "allow"
    assert evaluate(case("02_same_evidence_policy_v2_requires_review"), POLICY_V2)["reason_code"] == "PR_REVIEW_REQUIRED_EVIDENCE_MISSING"
    assert evaluate(case("03_threshold_changed"), POLICY_V2)["reason_code"] == "PR_REVIEW_RISK_THRESHOLD"
    assert evaluate(case("04_authority_rule_changed"), POLICY_V2)["reason_code"] == "PR_REVIEW_APPROVER_ROLE_REQUIRED"
    assert evaluate(case("05_blocked_under_both_scope_violation"), POLICY_V2)["reason_code"] == "PR_BLOCK_SCOPE_VIOLATION"
    assert evaluate(case("06_current_policy_would_allow_but_no_retroactive_effect"), POLICY_V2)["decision"] == "allow"


def test_replay_detects_policy_drift(tmp_path):
    runs = tmp_path / "runs"
    replay = tmp_path / "replay"
    run_suite(ROOT / "examples/demo_inputs", runs, ROOT / "policies/policy_v1.yml")
    reports = {r["case_id"]: r for r in replay_suite(runs, ROOT / "policies/policy_v2.yml", replay)}
    assert reports["01_allowed_under_policy_v1"]["drift_class"] == "NO_OUTCOME_CHANGE"
    assert reports["02_same_evidence_policy_v2_requires_review"]["drift_class"] == "PREVIOUSLY_ALLOWED_NOW_REVIEW"
    assert reports["03_threshold_changed"]["drift_class"] == "PREVIOUSLY_ALLOWED_NOW_REVIEW"
    assert reports["04_authority_rule_changed"]["drift_class"] == "PREVIOUSLY_ALLOWED_NOW_REVIEW"
    assert reports["05_blocked_under_both_scope_violation"]["drift_class"] == "NO_OUTCOME_CHANGE"
    assert reports["06_current_policy_would_allow_but_no_retroactive_effect"]["drift_class"] == "PREVIOUSLY_SUPPRESSED_NOW_ALLOWED"


def test_replay_does_not_create_retroactive_effect(tmp_path):
    runs = tmp_path / "runs"
    replay = tmp_path / "replay"
    run_suite(ROOT / "examples/demo_inputs", runs, ROOT / "policies/policy_v1.yml")
    no_effect_case = runs / "06_current_policy_would_allow_but_no_retroactive_effect"
    assert not (no_effect_case / "effect_record.json").exists()
    reports = {r["case_id"]: r for r in replay_suite(runs, ROOT / "policies/policy_v2.yml", replay)}
    report = reports["06_current_policy_would_allow_but_no_retroactive_effect"]
    assert report["replay_decision"]["effect_permitted"] is True
    assert report["effect_record_existed_before_replay"] is False
    assert report["effect_record_exists_after_replay"] is False
    assert report["effect_record_mutated"] is False
    assert not (no_effect_case / "effect_record.json").exists()


def test_tamper_detection_on_original_record(tmp_path):
    runs = tmp_path / "runs"
    run_suite(ROOT / "examples/demo_inputs", runs, ROOT / "policies/policy_v1.yml")
    receipt = runs / "01_allowed_under_policy_v1" / "decision_receipt.json"
    data = read_json(receipt)
    data["tampered_marker"] = True
    receipt.write_text(__import__("json").dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = verify_run(runs / "01_allowed_under_policy_v1", write_report=False)
    assert report["verified"] is False
    assert report["tamper_detected"] is True
