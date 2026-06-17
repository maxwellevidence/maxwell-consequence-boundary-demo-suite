"""Configuration snapshot helpers for the public Maxwell Effect Gate proof."""

from pathlib import Path
from typing import List


def write_config_snapshots(run_dir: Path, case: str, *, run_name: str | None = None) -> None:
    """Write public-safe original and effective configuration snapshots.

    These files are illustrative configuration artifacts for the public proof.
    They do not expose private Maxwell configuration, thresholds, or internal
    evaluator logic.
    """

    resolved_run_name = run_name or f"{case}_run"
    original_lines: List[str] = [
        "# Public-safe original workflow configuration snapshot",
        "workflow:",
        "  name: maxwell_effect_gate_public_proof",
        '  version: "0.3.0"',
        "  workflow_type: ai_assisted_cve_incident_research",
        "",
        "proof_scope:",
        "  bounded_downstream_effect: change_control_record_creation",
        "  replay_scope: evidence_and_decision_chain_only",
        "",
        "claims_boundary:",
        "  private_decision_core_disclosed: false",
        "  third_party_validation_claimed: false",
        "  production_readiness_claimed: false",
        "",
    ]

    effective_lines: List[str] = [
        "# Public-safe effective run configuration snapshot",
        "run:",
        f"  case: {case}",
        f"  run_name: {resolved_run_name}",
        "",
        "effect_gate:",
        "  decision_paths:",
        "    - allow",
        "    - pause",
        "    - block",
        "  downstream_effect: change_control_record_creation",
        "  policy_entrypoint: maxwell_effect_gate.policy_engine.evaluate_policy",
        "",
        "artifact_chain:",
        "  replay_scope: evidence_and_decision_chain_only",
        "  hash_manifest: artifact_hashes.sha256.txt",
        "  manifest_signature: artifact_hashes.sha256.txt.sig",
        "  manifest_public_key: ../../MANIFEST_PUBLIC_KEY.pem",
        "",
        "claims_boundary:",
        "  private_decision_core_disclosed: false",
        "  deterministic_model_replay_claimed: false",
        "  external_trust_root_claimed: false",
        "",
    ]

    (run_dir / "config_original.yml").write_text(
        "\n".join(original_lines) + "\n", encoding="utf-8"
    )
    (run_dir / "config_effective.yml").write_text(
        "\n".join(effective_lines) + "\n", encoding="utf-8"
    )
