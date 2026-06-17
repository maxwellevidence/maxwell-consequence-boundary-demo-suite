from __future__ import annotations

from typing import Any

from .paths import sha256_json
from .policy_engine import PolicyDecision
from .time_utils import utc_now


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_decision_receipt(
    case: dict[str, Any],
    evidence_bundle: dict[str, Any],
    authority_context: dict[str, Any],
    delegation_chain: dict[str, Any],
    decision: PolicyDecision,
    policy: dict[str, Any],
) -> dict[str, Any]:
    requested_effect = _as_dict(case.get("requested_effect"))
    task_handoff = _as_dict(case.get("task_handoff"))
    receipt = {
        "schema": "maxwell.multi_agent_authority.decision_receipt.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "outcome": decision.outcome,
        "lifecycle_state": decision.lifecycle_state,
        "reason_code": decision.reason_code,
        "effect_permitted": decision.effect_permitted,
        "review_route": decision.review_route,
        "explanation": decision.explanation,
        "authority_basis": decision.authority_basis,
        "risk_signal": decision.risk_signal,
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("policy_version"),
        "handoff_id": task_handoff.get("handoff_id"),
        "delegation_id": authority_context.get("delegation_id"),
        "evidence_bundle_id": evidence_bundle.get("bundle_id"),
        "delegation_chain_id": delegation_chain.get("delegation_chain_id"),
        "initiating_agent_id": authority_context.get("initiating_agent_id"),
        "executing_agent_id": authority_context.get("executing_agent_id"),
        "requested_scope": authority_context.get("requested_scope"),
        "requested_target_system": authority_context.get("requested_target_system"),
        "requested_effect_type": requested_effect.get("effect_type"),
        "evidence_continuity_ok": evidence_bundle.get("evidence_continuity_ok"),
        "created_at": utc_now(),
        "public_preview_note": "Decision receipt from simplified local multi-agent authority demo policy.",
    }
    receipt["decision_receipt_id"] = f"sha256:{sha256_json(receipt)}"
    return receipt
