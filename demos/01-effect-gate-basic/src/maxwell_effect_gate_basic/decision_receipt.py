from __future__ import annotations

from typing import Any

from .paths import sha256_json
from .policy_engine import PolicyDecision
from .time_utils import utc_now


def build_decision_receipt(
    case: dict[str, Any],
    evidence_bundle: dict[str, Any],
    authority_context: dict[str, Any],
    decision: PolicyDecision,
    policy: dict[str, Any],
) -> dict[str, Any]:
    receipt = {
        "schema": "maxwell.demo.decision_receipt.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "outcome": decision.outcome,
        "lifecycle_state": decision.lifecycle_state,
        "reason_code": decision.reason_code,
        "effect_permitted": decision.effect_permitted,
        "review_route": decision.review_route,
        "explanation": decision.explanation,
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("policy_version"),
        "evidence_bundle_id": evidence_bundle.get("bundle_id"),
        "authority_actor_id": authority_context.get("actor_id"),
        "target_scope": case.get("target_scope"),
        "created_at": utc_now(),
        "public_preview_note": "Decision receipt from simplified Maxwell Effect Gate Basic policy.",
    }
    receipt["decision_receipt_id"] = f"sha256:{sha256_json(receipt)}"
    return receipt
