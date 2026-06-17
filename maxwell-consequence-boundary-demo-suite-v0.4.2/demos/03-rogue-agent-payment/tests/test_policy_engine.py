from pathlib import Path

from maxwell_rogue_agent_payment.authority_context import build_authority_context
from maxwell_rogue_agent_payment.evidence_bundle import build_evidence_bundle
from maxwell_rogue_agent_payment.paths import read_json
from maxwell_rogue_agent_payment.policy_engine import evaluate_policy, load_policy

ROOT = Path(__file__).resolve().parents[1]
POLICY = load_policy(ROOT / "policies" / "payment_authority_policy.yml")
INPUTS = ROOT / "examples" / "demo_inputs"


def decision_for(example_name: str):
    case = read_json(INPUTS / example_name)
    evidence = build_evidence_bundle(case)
    authority = build_authority_context(case)
    return evaluate_policy(case, evidence, authority, POLICY)


def test_low_risk_invoice_is_permitted():
    decision = decision_for("01_low_risk_invoice_valid.json")
    assert decision.effect_permitted is True
    assert decision.lifecycle_state == "PAYMENT_EFFECT_COMMITTED"
    assert decision.reason_code == "PAYMENT_EFFECT_PERMITTED"


def test_high_value_payment_without_dual_control_routes_to_review():
    decision = decision_for("02_high_value_missing_dual_approval.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "PAYMENT_REVIEW_ROUTED"
    assert decision.reason_code == "PAYMENT_DUAL_CONTROL_REQUIRED"
    assert decision.review_route == "finance_dual_control_queue"


def test_vendor_bank_change_routes_to_review():
    decision = decision_for("03_suspicious_vendor_bank_change.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "PAYMENT_REVIEW_ROUTED"
    assert decision.reason_code == "PAYMENT_VENDOR_BANK_CHANGE_REVIEW"
    assert decision.review_route == "vendor_risk_review_queue"


def test_self_approval_suppresses_effect():
    decision = decision_for("04_self_approval_attempt.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "PAYMENT_EFFECT_SUPPRESSED"
    assert decision.reason_code == "PAYMENT_SELF_APPROVAL_SUPPRESSED"


def test_prompt_injection_attempt_cannot_create_payment_authority():
    decision = decision_for("05_prompt_injection_urgent_payment.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "PAYMENT_EFFECT_SUPPRESSED"
    assert decision.reason_code == "PAYMENT_PROMPT_INJECTION_SUPPRESSED"


def test_amount_exceeds_authority_limit_routes_to_review():
    decision = decision_for("06_amount_exceeds_authority_limit.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "PAYMENT_REVIEW_ROUTED"
    assert decision.reason_code == "PAYMENT_AMOUNT_EXCEEDS_AUTHORITY_LIMIT"
    assert decision.review_route == "finance_controller_review_queue"
