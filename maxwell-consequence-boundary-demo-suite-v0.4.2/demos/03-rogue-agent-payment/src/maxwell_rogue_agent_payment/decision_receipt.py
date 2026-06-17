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
    decision: PolicyDecision,
    policy: dict[str, Any],
) -> dict[str, Any]:
    payment = _as_dict(case.get("payment_request"))
    requested_effect = _as_dict(case.get("requested_effect"))
    receipt = {
        "schema": "maxwell.payment_demo.decision_receipt.v0.1",
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
        "evidence_bundle_id": evidence_bundle.get("bundle_id"),
        "authority_actor_id": authority_context.get("actor_id"),
        "payment_amount_usd": payment.get("amount_usd"),
        "invoice_id": payment.get("invoice_id"),
        "vendor_id": payment.get("vendor_id"),
        "vendor_bank_change": bool(payment.get("vendor_bank_change", False)),
        "target_scope": authority_context.get("requested_scope"),
        "target_system": requested_effect.get("target_system"),
        "created_at": utc_now(),
        "public_preview_note": "Decision receipt from simplified local payment demo policy.",
    }
    receipt["decision_receipt_id"] = f"sha256:{sha256_json(receipt)}"
    return receipt
