from pathlib import Path

from maxwell_effect_gate_basic.authority_context import build_authority_context
from maxwell_effect_gate_basic.evidence_bundle import build_evidence_bundle
from maxwell_effect_gate_basic.paths import read_json
from maxwell_effect_gate_basic.policy_engine import evaluate_policy, load_policy

ROOT = Path(__file__).resolve().parents[1]
POLICY = load_policy(ROOT / "policies" / "effect_gate_basic_policy.yml")
INPUTS = ROOT / "examples" / "demo_inputs"


def decision_for(example_name: str):
    case = read_json(INPUTS / example_name)
    evidence = build_evidence_bundle(case)
    authority = build_authority_context(case)
    return evaluate_policy(case, evidence, authority, POLICY)


def test_valid_low_risk_notice_is_permitted():
    decision = decision_for("01_valid_low_risk_notice.json")
    assert decision.effect_permitted is True
    assert decision.lifecycle_state == "EFFECT_COMMITTED"
    assert decision.reason_code == "EFFECT_GATE_EFFECT_PERMITTED"


def test_missing_evidence_routes_to_review():
    decision = decision_for("02_missing_evidence_refs.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "REVIEW_ROUTED"
    assert decision.reason_code == "EFFECT_GATE_REQUIRED_EVIDENCE_MISSING"


def test_missing_authority_context_routes_to_review():
    decision = decision_for("03_missing_authority_context.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "REVIEW_ROUTED"
    assert decision.reason_code == "EFFECT_GATE_AUTHORITY_CONTEXT_MISSING"


def test_scope_violation_suppresses_effect():
    decision = decision_for("04_scope_violation_suppressed.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "EFFECT_SUPPRESSED"
    assert decision.reason_code == "EFFECT_GATE_SCOPE_NOT_AUTHORIZED"


def test_high_risk_routes_to_review():
    decision = decision_for("05_high_risk_requires_review.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "REVIEW_ROUTED"
    assert decision.reason_code == "EFFECT_GATE_REVIEW_REQUIRED_HIGH_RISK"


def test_prompt_injection_attempt_cannot_create_authority():
    decision = decision_for("06_prompt_injection_suppressed.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "EFFECT_SUPPRESSED"
    assert decision.reason_code == "EFFECT_GATE_PROMPT_INJECTION_SUPPRESSED"
