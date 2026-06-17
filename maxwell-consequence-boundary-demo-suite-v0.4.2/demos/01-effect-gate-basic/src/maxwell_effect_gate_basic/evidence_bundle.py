from __future__ import annotations

from typing import Any

from .paths import sha256_json
from .time_utils import utc_now


def build_evidence_bundle(case: dict[str, Any]) -> dict[str, Any]:
    """Create a public-safe evidence bundle for a proposed action."""
    evidence_refs = case.get("evidence_refs") or []
    if not isinstance(evidence_refs, list):
        evidence_refs = []

    core_evidence = {
        "case_id": case.get("case_id"),
        "action_type": case.get("action_type"),
        "target_scope": case.get("target_scope"),
        "risk_level": case.get("risk_level"),
        "evidence_refs": evidence_refs,
        "requested_effect": case.get("requested_effect", {}),
    }

    return {
        "schema": "maxwell.demo.evidence_bundle.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "bundle_id": f"sha256:{sha256_json(core_evidence)}",
        "input_sha256": sha256_json(case),
        "evidence_refs": evidence_refs,
        "evidence_count": len(evidence_refs),
        "created_at": utc_now(),
        "public_preview_note": "Synthetic effect-gate evidence only; not a production evidence record.",
    }
