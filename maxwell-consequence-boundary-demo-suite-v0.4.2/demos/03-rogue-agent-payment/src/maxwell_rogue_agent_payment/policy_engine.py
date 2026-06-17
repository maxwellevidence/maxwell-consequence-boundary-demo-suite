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


def _routes(policy: dict[str, Any]) -> dict[str, str]:
    routes = policy.get("review_routes") or {}
    if not isinstance(routes, dict):
        return {}
    return {str(k): str(v) for k, v in routes.items()}


def _contains_prompt_injection_marker(case: dict[str, Any], policy: dict[str, Any]) -> bool:
    text = str(case.get("proposed_instruction", "")).lower()
    markers = policy.get("prompt_injection_markers") or []
    return any(str(marker).lower() in text for marker in markers)


def _payment(case: dict[str, Any]) -> dict[str, Any]:
    value = case.get("payment_request")
    return value if isinstance(value, dict) else {}


def _amount(payment: dict[str, Any]) -> float:
    try:
        return float(payment.get("amount_usd"))
    except (TypeError, ValueError):
        return 0.0


def _missing_required_evidence(evidence_bundle: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    present = set(evidence_bundle.get("evidence_types") or [])
    required = [str(item) for item in policy.get("required_evidence_types") or []]
    return [item for item in required if item not in present]


def evaluate_policy(
    case: dict[str, Any],
    evidence_bundle: dict[str, Any],
    authority_context: dict[str, Any],
    policy: dict[str, Any],
) -> PolicyDecision:
    """Evaluate the public payment-control policy.

    This function is intentionally deterministic and public-safe. It is not a
    production payment authorization engine.
    """
    routes = _routes(policy)
    payment = _payment(case)
    amount = _amount(payment)

    required_fields = policy.get("required_fields") or []
    missing_fields = [field for field in required_fields if field not in case]
    if missing_fields:
        return PolicyDecision(
            outcome="block",
            lifecycle_state="PAYMENT_EFFECT_SUPPRESSED",
            reason_code="PAYMENT_MALFORMED_INPUT",
            effect_permitted=False,
            explanation=f"Required fields missing: {', '.join(missing_fields)}.",
            authority_basis="input_missing_required_fields",
        )

    if amount <= 0:
        return PolicyDecision(
            outcome="block",
            lifecycle_state="PAYMENT_EFFECT_SUPPRESSED",
            reason_code="PAYMENT_MALFORMED_INPUT",
            effect_permitted=False,
            explanation="Payment amount is missing or not greater than zero.",
            authority_basis="invalid_payment_amount",
        )

    if _contains_prompt_injection_marker(case, policy):
        return PolicyDecision(
            outcome="block",
            lifecycle_state="PAYMENT_EFFECT_SUPPRESSED",
            reason_code="PAYMENT_PROMPT_INJECTION_SUPPRESSED",
            effect_permitted=False,
            explanation="Instruction text attempted to bypass payment controls. Output is not financial authority.",
            authority_basis="instruction_text_cannot_create_authority",
            risk_signal="prompt_injection_marker_detected",
        )

    allowed_vendor_statuses = set(policy.get("allowed_vendor_statuses") or [])
    if payment.get("vendor_status") not in allowed_vendor_statuses:
        return PolicyDecision(
            outcome="block",
            lifecycle_state="PAYMENT_EFFECT_SUPPRESSED",
            reason_code="PAYMENT_VENDOR_NOT_APPROVED",
            effect_permitted=False,
            explanation="Vendor status is not approved for payment effect under the demo policy.",
            authority_basis="vendor_status_not_approved",
            risk_signal="vendor_status",
        )

    missing_evidence = _missing_required_evidence(evidence_bundle, policy)
    minimum_refs = int(policy.get("minimum_evidence_refs", 0))
    if missing_evidence or evidence_bundle.get("evidence_count", 0) < minimum_refs:
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="PAYMENT_REVIEW_ROUTED",
            reason_code="PAYMENT_REQUIRED_EVIDENCE_MISSING",
            effect_permitted=False,
            explanation="Required payment evidence is missing: " + ", ".join(missing_evidence),
            review_route=routes.get("missing_evidence", "ap_review_queue"),
            authority_basis="evidence_incomplete",
            risk_signal="missing_payment_evidence",
        )

    if (
        not authority_context.get("authority_present")
        or not authority_context.get("can_approve_payment")
    ):
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="PAYMENT_REVIEW_ROUTED",
            reason_code="PAYMENT_AUTHORITY_CONTEXT_MISSING",
            effect_permitted=False,
            explanation="Payment authority context is missing or the claimed actor cannot approve payment.",
            review_route=routes.get("missing_authority", "finance_authority_review_queue"),
            authority_basis="approval_authority_missing_or_incomplete",
        )

    requested_scope = authority_context.get("requested_scope")
    allowed_scopes = set(authority_context.get("allowed_payment_scopes") or [])
    if requested_scope not in allowed_scopes:
        return PolicyDecision(
            outcome="block",
            lifecycle_state="PAYMENT_EFFECT_SUPPRESSED",
            reason_code="PAYMENT_SCOPE_NOT_AUTHORIZED",
            effect_permitted=False,
            explanation="The requested payment scope is outside the actor's claimed authority.",
            authority_basis="scope_not_authorized",
        )

    if authority_context.get("self_approval_detected"):
        return PolicyDecision(
            outcome="block",
            lifecycle_state="PAYMENT_EFFECT_SUPPRESSED",
            reason_code="PAYMENT_SELF_APPROVAL_SUPPRESSED",
            effect_permitted=False,
            explanation="Requester and approver are the same actor. Self-approval cannot create payment effect.",
            authority_basis="self_approval_detected",
            risk_signal="segregation_of_duties",
        )

    approval_limit = float(authority_context.get("approval_limit_usd") or 0.0)
    if amount > approval_limit:
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="PAYMENT_REVIEW_ROUTED",
            reason_code="PAYMENT_AMOUNT_EXCEEDS_AUTHORITY_LIMIT",
            effect_permitted=False,
            explanation="Payment amount exceeds the claimed approver's authority limit.",
            review_route=routes.get("amount_limit", "finance_controller_review_queue"),
            authority_basis="amount_exceeds_approval_limit",
            risk_signal="approval_limit_exceeded",
        )

    dual_threshold = float(policy.get("dual_control_threshold_usd", 0.0))
    if amount >= dual_threshold and not authority_context.get("dual_approval_present"):
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="PAYMENT_REVIEW_ROUTED",
            reason_code="PAYMENT_DUAL_CONTROL_REQUIRED",
            effect_permitted=False,
            explanation="Payment amount crosses the dual-control threshold and lacks second approval.",
            review_route=routes.get("dual_control", "finance_dual_control_queue"),
            authority_basis="dual_control_required",
            risk_signal="high_value_payment",
        )

    if bool(payment.get("vendor_bank_change", False)) and bool(
        policy.get("bank_change_review_required", True)
    ):
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="PAYMENT_REVIEW_ROUTED",
            reason_code="PAYMENT_VENDOR_BANK_CHANGE_REVIEW",
            effect_permitted=False,
            explanation="Vendor bank-account change requires controlled review before payment effect.",
            review_route=routes.get("vendor_bank_change", "vendor_risk_review_queue"),
            authority_basis="vendor_bank_change_requires_review",
            risk_signal="vendor_bank_change",
        )

    risk_level = str(case.get("risk_level", "")).lower()
    review_levels = set(policy.get("review_required_risk_levels") or [])
    if risk_level in review_levels:
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="PAYMENT_REVIEW_ROUTED",
            reason_code="PAYMENT_REVIEW_REQUIRED_RISK",
            effect_permitted=False,
            explanation="Payment risk level requires controlled review before effect.",
            review_route=routes.get("risk", "finance_review_queue"),
            authority_basis="risk_level_requires_review",
            risk_signal="risk_level",
        )

    allowed_levels = set(policy.get("allowed_risk_levels") or [])
    if risk_level in allowed_levels:
        return PolicyDecision(
            outcome="allow",
            lifecycle_state="PAYMENT_EFFECT_COMMITTED",
            reason_code="PAYMENT_EFFECT_PERMITTED",
            effect_permitted=True,
            explanation="Evidence, vendor status, scope, amount, and authority were sufficient for this public demo policy.",
            authority_basis="evidence_and_authority_sufficient",
        )

    return PolicyDecision(
        outcome="hold",
        lifecycle_state="PAYMENT_REVIEW_ROUTED",
        reason_code="PAYMENT_REVIEW_REQUIRED_RISK",
        effect_permitted=False,
        explanation="Risk level is not explicitly auto-permitted by the demo policy.",
        review_route=routes.get("risk", "finance_review_queue"),
        authority_basis="risk_not_auto_permitted",
        risk_signal="risk_level_unknown",
    )
