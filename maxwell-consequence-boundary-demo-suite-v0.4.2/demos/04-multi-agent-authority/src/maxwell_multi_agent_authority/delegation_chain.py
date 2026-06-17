from __future__ import annotations

from typing import Any

from .paths import sha256_json
from .time_utils import utc_now


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_delegation_chain(
    case: dict[str, Any], evidence_bundle: dict[str, Any], authority_context: dict[str, Any]
) -> dict[str, Any]:
    initiating_agent = _as_dict(case.get("initiating_agent"))
    executing_agent = _as_dict(case.get("executing_agent"))
    task_handoff = _as_dict(case.get("task_handoff"))
    delegation = _as_dict(case.get("claimed_delegation"))

    chain = {
        "schema": "maxwell.multi_agent_authority.delegation_chain.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "handoff_id": task_handoff.get("handoff_id"),
        "delegation_id": delegation.get("delegation_id"),
        "from_agent_id": initiating_agent.get("agent_id"),
        "to_agent_id": executing_agent.get("agent_id"),
        "handoff_scope": task_handoff.get("task_scope"),
        "requested_scope": authority_context.get("requested_scope"),
        "requested_target_system": authority_context.get("requested_target_system"),
        "evidence_bundle_id": evidence_bundle.get("bundle_id"),
        "evidence_continuity_ok": evidence_bundle.get("evidence_continuity_ok"),
        "delegation_participants_match": authority_context.get("delegation_participants_match"),
        "handoff_participants_match": authority_context.get("handoff_participants_match"),
        "created_at": utc_now(),
        "public_preview_note": "Synthetic public-safe delegation chain for demo review.",
    }
    chain["delegation_chain_id"] = f"sha256:{sha256_json(chain)}"
    return chain
