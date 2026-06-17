from __future__ import annotations

from typing import Any


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _float_or_zero(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build_authority_context(case: dict[str, Any]) -> dict[str, Any]:
    """Extract public-safe payment authority context from a proposed payment action."""
    authority = _as_dict(case.get("claimed_authority"))
    approval_chain = _as_dict(case.get("approval_chain"))
    payment = _as_dict(case.get("payment_request"))
    requested_effect = _as_dict(case.get("requested_effect"))

    allowed_scopes = [str(scope) for scope in _as_list(authority.get("allowed_payment_scopes"))]
    requester_id = approval_chain.get("requester_id")
    primary_approver_id = approval_chain.get("primary_approver_id")
    secondary_approver_id = approval_chain.get("secondary_approver_id")
    actor_id = authority.get("actor_id")
    requested_scope = case.get("target_scope") or requested_effect.get("target_scope")

    return {
        "schema": "maxwell.payment_demo.authority_context.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "actor_id": actor_id,
        "role": authority.get("role"),
        "can_request_payment": bool(authority.get("can_request_payment", False)),
        "can_approve_payment": bool(authority.get("can_approve_payment", False)),
        "approval_limit_usd": _float_or_zero(authority.get("approval_limit_usd")),
        "allowed_payment_scopes": allowed_scopes,
        "delegation_id": authority.get("delegation_id"),
        "request_amount_usd": _float_or_zero(payment.get("amount_usd")),
        "requested_scope": requested_scope,
        "target_system": requested_effect.get("target_system"),
        "requester_id": requester_id,
        "primary_approver_id": primary_approver_id,
        "secondary_approver_id": secondary_approver_id,
        "dual_approval_present": bool(approval_chain.get("dual_approval_present", False)),
        "self_approval_detected": bool(
            requester_id
            and primary_approver_id
            and str(requester_id) == str(primary_approver_id)
        ),
        "authority_present": bool(authority),
        "public_preview_note": "Synthetic payment authority context only; not a production authorization record.",
    }
