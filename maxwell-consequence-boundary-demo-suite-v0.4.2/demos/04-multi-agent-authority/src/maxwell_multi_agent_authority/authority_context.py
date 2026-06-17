from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _str_list(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value)]


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _expired(expires_at: Any, evaluation_time: Any) -> bool:
    exp = _parse_time(expires_at)
    eva = _parse_time(evaluation_time) or datetime.now(UTC)
    if exp is None:
        return False
    return exp < eva


def build_authority_context(case: dict[str, Any]) -> dict[str, Any]:
    """Extract delegated authority context from a proposed multi-agent handoff."""
    initiating_agent = _as_dict(case.get("initiating_agent"))
    executing_agent = _as_dict(case.get("executing_agent"))
    task_handoff = _as_dict(case.get("task_handoff"))
    delegation = _as_dict(case.get("claimed_delegation"))
    requested_effect = _as_dict(case.get("requested_effect"))

    delegated_scopes = _str_list(delegation.get("delegated_scopes"))
    delegated_target_systems = _str_list(delegation.get("target_systems"))
    executing_local_scopes = _str_list(executing_agent.get("local_authority_scopes"))
    initiating_scopes = _str_list(initiating_agent.get("authority_scopes"))

    requested_scope = requested_effect.get("target_scope") or task_handoff.get("task_scope")
    handoff_scope = task_handoff.get("task_scope")
    requested_target_system = requested_effect.get("target_system") or task_handoff.get("target_system")

    from_matches = task_handoff.get("from_agent_id") == initiating_agent.get("agent_id")
    to_matches = task_handoff.get("to_agent_id") == executing_agent.get("agent_id")
    delegator_matches = delegation.get("delegator_agent_id") == initiating_agent.get("agent_id")
    delegatee_matches = delegation.get("delegatee_agent_id") == executing_agent.get("agent_id")

    task_expansion_detected = bool(
        handoff_scope
        and requested_scope
        and requested_scope != handoff_scope
        and requested_scope not in delegated_scopes
    )

    return {
        "schema": "maxwell.multi_agent_authority.authority_context.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "initiating_agent_id": initiating_agent.get("agent_id"),
        "executing_agent_id": executing_agent.get("agent_id"),
        "initiating_agent_role": initiating_agent.get("role"),
        "executing_agent_role": executing_agent.get("role"),
        "handoff_id": task_handoff.get("handoff_id"),
        "handoff_scope": handoff_scope,
        "requested_scope": requested_scope,
        "requested_target_system": requested_target_system,
        "risk_level": requested_effect.get("risk_level") or task_handoff.get("risk_level"),
        "delegation_present": bool(delegation.get("present", False)),
        "delegation_id": delegation.get("delegation_id"),
        "delegated_scopes": delegated_scopes,
        "delegated_target_systems": delegated_target_systems,
        "delegation_expires_at": delegation.get("expires_at"),
        "delegation_expired": _expired(delegation.get("expires_at"), case.get("evaluation_time")),
        "may_execute_downstream_effect": bool(
            delegation.get("may_execute_downstream_effect", False)
        ),
        "initiating_agent_may_delegate": bool(initiating_agent.get("may_delegate", False)),
        "initiating_agent_authority_scopes": initiating_scopes,
        "executing_agent_local_authority_scopes": executing_local_scopes,
        "handoff_participants_match": bool(from_matches and to_matches),
        "delegation_participants_match": bool(delegator_matches and delegatee_matches),
        "requested_scope_in_delegation": requested_scope in delegated_scopes,
        "requested_target_system_in_delegation": requested_target_system in delegated_target_systems,
        "executor_has_local_authority_for_scope": requested_scope in executing_local_scopes,
        "task_expansion_detected": task_expansion_detected,
        "authority_present": bool(delegation),
        "public_preview_note": "Synthetic delegated authority context only; not a production authorization record.",
    }
