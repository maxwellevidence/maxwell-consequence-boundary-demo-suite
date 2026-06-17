"""Workflow output builder for the public Maxwell Effect Gate proof."""

from typing import Any, Dict


def build_workflow_output() -> Dict[str, Any]:
    """Build a simulated AI-assisted workflow output.

    This public proof does not claim technical correctness of the CVE analysis.
    The workflow output exists to show what the AI-assisted workflow attempted
    to propose before the Maxwell effect gate evaluated downstream effect.
    """

    return {
        "workflow_output_id": "WF-OUT-2026-1043-PAYMENTS-API",
        "workflow_type": "ai_assisted_cve_incident_research",
        "target_system": "payments-api",
        "cve_id": "CVE-2026-1043",
        "summary": (
            "Simulated AI-assisted workflow output prepared a bounded "
            "remediation proposal for Maxwell authority review."
        ),
        "proposed_downstream_action": "create_change_control_record",
        "downstream_effect_not_self_authorized": True,
        "requires_effect_gate_review": True,
        "claims_boundary": [
            "This workflow output is simulated.",
            "This proof does not validate remediation correctness.",
            "This proof does not replay model calls or external CVE source state."
        ]
    }
