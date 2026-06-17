"""Artifact writer for the public Maxwell Effect Gate proof."""

import json
from pathlib import Path
from typing import Any, Dict


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    """Write a JSON artifact with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        file.write("\n")


def write_run_artifacts(
    run_dir: Path,
    action_proposal: Dict[str, Any],
    evidence_bundle: Dict[str, Any],
    authority_context: Dict[str, Any],
    decision_receipt: Dict[str, Any],
) -> None:
    """Write the inspectable public artifact chain for one run."""

    write_json(run_dir / "action_proposal.json", action_proposal)
    write_json(run_dir / "evidence_bundle.json", evidence_bundle)
    write_json(run_dir / "authority_context.json", authority_context)
    write_json(run_dir / "decision_receipt.json", decision_receipt)

    if decision_receipt["decision"] == "allow":
        write_json(
            run_dir / "effect_record.json",
            {
                "effect_record_id": "CHANGE-RECORD-2026-1043",
                "effect_type": "change_control_record",
                "status": "created",
                "created_because": "Maxwell effect gate returned allow",
                "source_decision_receipt": "decision_receipt.json",
            },
        )

    if decision_receipt["decision"] == "pause":
        write_json(
            run_dir / "interaction_or_oauth_required.json",
            {
                "status": "required",
                "reason": "Additional authority is required before downstream effect.",
                "source_decision_receipt": "decision_receipt.json",
            },
        )
