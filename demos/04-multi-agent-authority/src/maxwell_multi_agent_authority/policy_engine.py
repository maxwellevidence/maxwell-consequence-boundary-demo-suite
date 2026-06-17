from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PolicyDecision:
    outcome: str
    lifecycle_state: str
    reason_code: str
    effect_permitted: bool
    explanation: str
    review_route: str | None = None
    authority_basis: str | None = None
    risk_signal: str | None = None


def load_policy(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Policy file must contain a mapping: {path}")
    return data


def _contains_prompt_injection_marker(case: dict[str, Any], policy: dict[str, Any]) -> bool:
    text = str(case.get("proposed_instruction", "")).lower()
    markers = policy.get("prompt_injection_markers") or []
    return any(str(marker).lower() in text for marker in markers)


def _review_route(policy: dict[str, Any], key: str, fallback: str) -> str:
    routes = policy.get("review_routes") or {}
    return str(routes.get(key, fallback))


def evaluate_policy(
    case: dict[str, Any],
    evidence_bundle: dict[str, Any],
    authority_context: dict[str, Any],
    policy: dict[str, Any],
) -> PolicyDecision:
    required_fields = policy.get("required_fields") or []
    missing = [field for field in required_fields if field not in case]
    if missing:
        return PolicyDecision(
            outcome="block",
            lifecycle_state="DELEGATED_EFFECT_SUPPRESSED",
            reason_code="MULTI_AGENT_MALFORMED_INPUT",
            effect_permitted=False,
            explanation=f"Required fields missing: {', '.join(missing)}.",
            authority_basis="malformed_request_cannot_create_delegation",
            risk_signal="malformed_input",
        )

    if _contains_prompt_injection_marker(case, policy):
        return PolicyDecision(
            outcome="block",
            lifecycle_state="DELEGATED_EFFECT_SUPPRESSED",
            reason_code="DELEGATION_PROMPT_INJECTION_SUPPRESSED",
            effect_permitted=False,
            explanation="Instruction text attempted to bypass or manufacture delegated authority.",
            authority_basis="instruction_text_cannot_create_delegation",
            risk_signal="prompt_injection_boundary",
        )

    if not evidence_bundle.get("evidence_continuity_ok"):
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="DELEGATION_REVIEW_ROUTED",
            reason_code="DELEGATION_EVIDENCE_PACKET_MISSING",
            effect_permitted=False,
            explanation="Evidence packet is missing, empty, or not bound to the claimed delegation.",
            review_route=_review_route(policy, "evidence_continuity", "evidence_continuity_review_queue"),
            authority_basis="evidence_continuity_not_sufficient",
            risk_signal="evidence_continuity_break",
        )

    if not authority_context.get("delegation_present"):
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="DELEGATION_REVIEW_ROUTED",
            reason_code="DELEGATION_CHAIN_MISSING_REVIEW",
            effect_permitted=False,
            explanation="No claimed delegation was supplied with the handoff.",
            review_route=_review_route(policy, "authority_scope", "authority_scope_review_queue"),
            authority_basis="delegation_missing",
            risk_signal="delegation_absent",
        )

    if not authority_context.get("handoff_participants_match") or not authority_context.get(
        "delegation_participants_match"
    ):
        return PolicyDecision(
            outcome="block",
            lifecycle_state="DELEGATED_EFFECT_SUPPRESSED",
            reason_code="DELEGATION_CHAIN_MISMATCH_SUPPRESSED",
            effect_permitted=False,
            explanation="Handoff participants and claimed delegation participants do not align.",
            authority_basis="delegation_chain_identity_mismatch",
            risk_signal="identity_chain_mismatch",
        )

    if authority_context.get("delegation_expired"):
        return PolicyDecision(
            outcome="block",
            lifecycle_state="DELEGATED_EFFECT_SUPPRESSED",
            reason_code="DELEGATION_EXPIRED_SUPPRESSED",
            effect_permitted=False,
            explanation="The claimed delegation expired before evaluation time.",
            authority_basis="delegation_expired",
            risk_signal="expired_delegation",
        )

    if not authority_context.get("may_execute_downstream_effect"):
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="DELEGATION_REVIEW_ROUTED",
            reason_code="DELEGATION_EXECUTION_NOT_GRANTED_REVIEW",
            effect_permitted=False,
            explanation="The delegation does not explicitly permit downstream effect execution.",
            review_route=_review_route(policy, "authority_scope", "authority_scope_review_queue"),
            authority_basis="delegation_does_not_grant_execution",
            risk_signal="execution_right_missing",
        )

    if not authority_context.get("requested_scope_in_delegation"):
        if authority_context.get("task_expansion_detected"):
            return PolicyDecision(
                outcome="block",
                lifecycle_state="DELEGATED_EFFECT_SUPPRESSED",
                reason_code="AGENT_SCOPE_EXPANSION_SUPPRESSED",
                effect_permitted=False,
                explanation="The executing agent expanded the requested effect beyond the delegated task scope.",
                authority_basis="requested_scope_outside_delegation",
                risk_signal="cross_agent_scope_expansion",
            )
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="DELEGATION_REVIEW_ROUTED",
            reason_code="DELEGATION_SCOPE_MISSING_REVIEW",
            effect_permitted=False,
            explanation="Delegation exists but does not include the requested downstream scope.",
            review_route=_review_route(policy, "authority_scope", "authority_scope_review_queue"),
            authority_basis="requested_scope_not_delegated",
            risk_signal="delegated_scope_missing",
        )

    if not authority_context.get("requested_target_system_in_delegation"):
        return PolicyDecision(
            outcome="block",
            lifecycle_state="DELEGATED_EFFECT_SUPPRESSED",
            reason_code="DELEGATION_WRONG_SYSTEM_SUPPRESSED",
            effect_permitted=False,
            explanation="Delegated authority was reused for a target system outside the handoff boundary.",
            authority_basis="requested_target_system_not_delegated",
            risk_signal="wrong_system_authority_reuse",
        )

    risk_level = str(authority_context.get("risk_level", "")).lower()
    review_levels = set(str(item).lower() for item in policy.get("review_required_risk_levels") or [])
    if risk_level in review_levels:
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="DELEGATION_REVIEW_ROUTED",
            reason_code="DELEGATION_HIGH_RISK_REVIEW",
            effect_permitted=False,
            explanation="Risk level requires review before delegated downstream effect.",
            review_route=_review_route(policy, "high_risk", "multi_agent_governance_review_queue"),
            authority_basis="risk_requires_review",
            risk_signal="high_risk_delegated_effect",
        )

    return PolicyDecision(
        outcome="allow",
        lifecycle_state="DELEGATED_EFFECT_COMMITTED",
        reason_code="DELEGATED_EFFECT_PERMITTED",
        effect_permitted=True,
        explanation="Delegation, evidence continuity, scope, and target system were sufficient.",
        authority_basis="valid_delegation_with_evidence_continuity",
        risk_signal="delegated_effect_within_scope",
    )
