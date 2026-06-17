from pathlib import Path

from maxwell_multi_agent_authority.authority_context import build_authority_context
from maxwell_multi_agent_authority.evidence_bundle import build_evidence_bundle
from maxwell_multi_agent_authority.paths import read_json
from maxwell_multi_agent_authority.policy_engine import evaluate_policy, load_policy

ROOT = Path(__file__).resolve().parents[1]
POLICY = load_policy(ROOT / "policies" / "multi_agent_authority_policy.yml")
INPUTS = ROOT / "examples" / "demo_inputs"


def decision_for(example_name: str):
    case = read_json(INPUTS / example_name)
    evidence = build_evidence_bundle(case)
    authority = build_authority_context(case)
    return evaluate_policy(case, evidence, authority, POLICY)


def test_valid_delegated_handoff_is_permitted():
    decision = decision_for("01_valid_delegated_handoff.json")
    assert decision.effect_permitted is True
    assert decision.lifecycle_state == "DELEGATED_EFFECT_COMMITTED"
    assert decision.reason_code == "DELEGATED_EFFECT_PERMITTED"


def test_missing_authority_scope_routes_to_review():
    decision = decision_for("02_handoff_missing_authority_scope.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "DELEGATION_REVIEW_ROUTED"
    assert decision.reason_code == "DELEGATION_SCOPE_MISSING_REVIEW"
    assert decision.review_route == "authority_scope_review_queue"


def test_scope_expansion_is_suppressed():
    decision = decision_for("03_agent_expands_task_beyond_scope.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "DELEGATED_EFFECT_SUPPRESSED"
    assert decision.reason_code == "AGENT_SCOPE_EXPANSION_SUPPRESSED"


def test_wrong_system_authority_reuse_is_suppressed():
    decision = decision_for("04_wrong_system_authority_reuse.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "DELEGATED_EFFECT_SUPPRESSED"
    assert decision.reason_code == "DELEGATION_WRONG_SYSTEM_SUPPRESSED"


def test_lost_evidence_packet_routes_to_review():
    decision = decision_for("05_handoff_loses_evidence_packet.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "DELEGATION_REVIEW_ROUTED"
    assert decision.reason_code == "DELEGATION_EVIDENCE_PACKET_MISSING"
    assert decision.review_route == "evidence_continuity_review_queue"


def test_prompt_injection_cannot_create_delegated_authority():
    decision = decision_for("06_prompt_injection_handoff_override.json")
    assert decision.effect_permitted is False
    assert decision.lifecycle_state == "DELEGATED_EFFECT_SUPPRESSED"
    assert decision.reason_code == "DELEGATION_PROMPT_INJECTION_SUPPRESSED"
    assert decision.authority_basis == "instruction_text_cannot_create_delegation"
