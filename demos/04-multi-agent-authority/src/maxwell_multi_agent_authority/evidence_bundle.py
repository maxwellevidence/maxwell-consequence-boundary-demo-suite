from __future__ import annotations

from typing import Any

from .paths import sha256_json
from .time_utils import utc_now


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_evidence_bundle(case: dict[str, Any]) -> dict[str, Any]:
    """Create a public-safe evidence bundle for a multi-agent handoff."""
    evidence_packet = _as_dict(case.get("evidence_packet"))
    claimed_delegation = _as_dict(case.get("claimed_delegation"))
    task_handoff = _as_dict(case.get("task_handoff"))
    refs = [str(ref) for ref in _as_list(evidence_packet.get("refs"))]

    evidence_present = bool(evidence_packet.get("present", False))
    packet_id = evidence_packet.get("packet_id")
    claimed_packet_id = claimed_delegation.get("evidence_packet_id")
    continuity_ok = bool(evidence_present and packet_id and claimed_packet_id == packet_id and refs)

    core = {
        "case_id": case.get("case_id"),
        "packet_id": packet_id,
        "handoff_id": task_handoff.get("handoff_id"),
        "refs": refs,
        "continuity_ok": continuity_ok,
        "requested_effect": case.get("requested_effect", {}),
    }

    return {
        "schema": "maxwell.multi_agent_authority.evidence_bundle.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "bundle_id": f"sha256:{sha256_json(core)}",
        "input_sha256": sha256_json(case),
        "packet_id": packet_id,
        "evidence_refs": refs,
        "evidence_count": len(refs),
        "evidence_packet_present": evidence_present,
        "claimed_delegation_packet_id": claimed_packet_id,
        "evidence_continuity_ok": continuity_ok,
        "handoff_id": task_handoff.get("handoff_id"),
        "created_at": utc_now(),
        "public_preview_note": "Synthetic handoff evidence only; not a production evidence record.",
    }
