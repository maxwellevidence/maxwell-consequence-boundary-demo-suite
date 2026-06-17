"""Decision surface output builder for the public Maxwell Effect Gate proof."""

from typing import Any, Dict


def build_decision_surface_output(decision_receipt: Dict[str, Any]) -> Dict[str, Any]:
    """Build a public-facing decision surface output.

    This is the simplified output a downstream system would inspect before
    deciding whether to create the bounded effect record.
    """

    decision = decision_receipt["decision"]

    return {
        "decision": decision,
        "downstream_effect_allowed": decision_receipt["downstream_effect_allowed"],
        "effect_boundary": decision_receipt["effect_boundary"],
        "reason_codes": decision_receipt["reason_codes"],
        "downstream_instruction": _instruction_for_decision(decision),
        "receipt_reference": "decision_receipt.json",
        "claims_boundary": (
            "Public decision surface only. This does not disclose Maxwell's "
            "private authority model, evaluator chain, scoring rules, or thresholds."
        ),
    }


def _instruction_for_decision(decision: str) -> str:
    """Return the downstream instruction for a public proof decision."""

    if decision == "allow":
        return "create_bounded_change_control_record"

    if decision == "pause":
        return "hold_effect_pending_additional_authority"

    return "refuse_downstream_effect"
