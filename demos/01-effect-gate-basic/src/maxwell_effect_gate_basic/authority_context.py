from __future__ import annotations

from typing import Any


def build_authority_context(case: dict[str, Any]) -> dict[str, Any]:
    """Extract public-safe authority context from a proposed action."""
    authority = case.get("claimed_authority") or {}
    if not isinstance(authority, dict):
        authority = {}

    allowed_scopes = authority.get("allowed_scopes") or []
    if not isinstance(allowed_scopes, list):
        allowed_scopes = []

    return {
        "schema": "maxwell.demo.authority_context.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "actor_id": authority.get("actor_id"),
        "role": authority.get("role"),
        "can_execute": bool(authority.get("can_execute", False)),
        "allowed_scopes": allowed_scopes,
        "delegation_id": authority.get("delegation_id"),
        "target_scope": case.get("target_scope"),
        "authority_present": bool(authority),
        "public_preview_note": "Synthetic effect-gate authority context only; not a production authorization record.",
    }
