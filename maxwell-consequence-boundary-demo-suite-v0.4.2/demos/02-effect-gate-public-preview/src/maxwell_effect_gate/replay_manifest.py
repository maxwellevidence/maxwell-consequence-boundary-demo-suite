"""Replay manifest builder for the public Maxwell Effect Gate proof."""

from pathlib import Path
from typing import Any, Dict, List


def build_replay_manifest(
    run_name: str,
    decision_receipt: Dict[str, Any],
    run_dir: Path,
) -> Dict[str, Any]:
    """Build a replay manifest for the evidence-and-decision chain.

    Replay in this public proof means replay of the artifact chain,
    not deterministic replay of model calls, external CVE data, or live tool state.
    """

    artifacts: List[str] = sorted(path.name for path in run_dir.glob("*.json"))

    return {
        "run_name": run_name,
        "decision": decision_receipt["decision"],
        "replay_scope": "evidence_and_decision_chain_only",
        "not_replayed": [
            "model_call_outputs",
            "external_cve_source_state",
            "live_tool_state"
        ],
        "artifacts": artifacts,
        "verification_note": (
            "Inspect the proposal, evidence bundle, authority context, "
            "decision receipt, optional effect record, and SHA-256 manifest."
        )
    }
