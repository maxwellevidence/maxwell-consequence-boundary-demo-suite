"""Action proposal builder for the public Maxwell Effect Gate proof."""

from typing import Any, Dict


def build_action_proposal(**overrides: Any) -> Dict[str, Any]:
    """Build a simulated CVE remediation change proposal.

    The returned object contains both reviewer-readable proposal metadata and
    the explicit policy fields the gate evaluates. The proof is not about
    whether the CVE remediation is technically correct; it is about whether a
    proposed downstream effect is admitted by policy.
    """

    proposal = {
        "proposal_id": "PROP-2026-1043-PAYMENTS-API",
        "source_prompt": "examples/requests/shared_prompt.txt",
        "workflow_type": "ai_assisted_cve_incident_research",
        "target_system": "payments-api",
        "proposed_action": "create_change_control_record",
        "proposed_change_summary": (
            "Prepare a bounded remediation change-control record for "
            "payments-api based on simulated CVE research output."
        ),
        "effect_surface": "change_control_record",
        "requested_environment": "staging",
        # Policy-evaluated fields.
        "action_type": "create_change_control_record",
        "target_environment": "staging",
        "risk_level": "low",
        "requester_id": "requester@example.test",
        "approver_id": "approver@example.test",
        "dual_control_present": True,
    }
    proposal.update(overrides)
    proposal["requested_environment"] = proposal["target_environment"]
    return proposal
