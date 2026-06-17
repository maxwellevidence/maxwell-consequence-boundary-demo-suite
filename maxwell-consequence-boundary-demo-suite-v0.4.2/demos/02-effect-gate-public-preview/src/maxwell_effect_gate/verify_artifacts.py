"""Verify generated Maxwell Effect Gate public proof artifacts.

This verifier checks the public artifact chain after `make demo` has generated
artifacts. It verifies both local SHA-256 hashes and the RSA signature over
the hash manifest against the repo-root manifest public key.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from maxwell_effect_gate.hashing import (
    HASHED_SUFFIXES,
    MANIFEST_NAME,
    MANIFEST_SIGNATURE_NAME,
    sha256_file,
    verify_hash_manifest_signature,
)
from maxwell_effect_gate.run_demo import ARTIFACTS_DIR, VALID_CASES


COMMON_REQUIRED_ARTIFACTS = [
    "action_proposal.json",
    "evidence_bundle.json",
    "authority_context.json",
    "workflow_output.json",
    "decision_surface_output.json",
    "decision_receipt.json",
    "config_original.yml",
    "config_effective.yml",
    "workflow_profiling_metrics.json",
    "replay_manifest.json",
    MANIFEST_NAME,
    MANIFEST_SIGNATURE_NAME,
]

RUNS = [f"{case}_run" for case in VALID_CASES]


def expected_hashed_artifacts(run_dir: Path) -> List[str]:
    """Return files that should be listed in the hash manifest."""

    return sorted(
        path.name
        for path in run_dir.iterdir()
        if path.is_file() and path.suffix in HASHED_SUFFIXES
    )


def _read_manifest(run_dir: Path) -> Dict[str, str]:
    """Read artifact_hashes.sha256.txt into a filename-to-hash mapping."""

    manifest_path = run_dir / MANIFEST_NAME
    manifest: Dict[str, str] = {}

    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        digest, filename = line.split(maxsplit=1)
        manifest[filename.strip()] = digest.strip()

    return manifest


def _read_decision(run_dir: Path) -> str | None:
    receipt_path = run_dir / "decision_receipt.json"
    if not receipt_path.exists():
        return None
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    decision = receipt.get("decision")
    return decision if isinstance(decision, str) else None


def verify_run(run_name: str) -> List[str]:
    """Verify one generated run folder.

    Returns a list of error messages. An empty list means the run passed.
    """

    errors: List[str] = []
    run_dir = ARTIFACTS_DIR / run_name

    if not run_dir.exists():
        return [f"{run_name}: missing run directory"]

    for artifact_name in COMMON_REQUIRED_ARTIFACTS:
        if not (run_dir / artifact_name).exists():
            errors.append(f"{run_name}: missing {artifact_name}")

    decision = _read_decision(run_dir)
    if decision == "allow":
        if not (run_dir / "effect_record.json").exists():
            errors.append(f"{run_name}: missing effect_record.json")
        if (run_dir / "interaction_or_oauth_required.json").exists():
            errors.append(f"{run_name}: interaction_or_oauth_required.json must not exist after allow")
    elif decision == "pause":
        if (run_dir / "effect_record.json").exists():
            errors.append(f"{run_name}: effect_record.json must not exist")
        if not (run_dir / "interaction_or_oauth_required.json").exists():
            errors.append(f"{run_name}: missing interaction_or_oauth_required.json")
    elif decision == "block":
        if (run_dir / "effect_record.json").exists():
            errors.append(f"{run_name}: effect_record.json must not exist")
        if (run_dir / "interaction_or_oauth_required.json").exists():
            errors.append(f"{run_name}: interaction_or_oauth_required.json must not exist after block")
    else:
        errors.append(f"{run_name}: invalid or missing decision")

    manifest_path = run_dir / MANIFEST_NAME
    if not manifest_path.exists():
        errors.append(f"{run_name}: missing {MANIFEST_NAME}")
        return errors

    if not verify_hash_manifest_signature(run_dir):
        errors.append(f"{run_name}: manifest signature verification failed")

    manifest = _read_manifest(run_dir)

    for artifact_name in expected_hashed_artifacts(run_dir):
        if artifact_name not in manifest:
            errors.append(f"{run_name}: manifest missing {artifact_name}")

    for artifact_name, expected_digest in manifest.items():
        artifact_path = run_dir / artifact_name

        if not artifact_path.exists():
            errors.append(f"{run_name}: manifest references missing {artifact_name}")
            continue

        actual_digest = sha256_file(artifact_path)

        if actual_digest != expected_digest:
            errors.append(f"{run_name}: hash mismatch for {artifact_name}")

    return errors


def main() -> None:
    """Verify all generated public proof artifacts."""

    all_errors: List[str] = []

    for run_name in RUNS:
        all_errors.extend(verify_run(run_name))

    if all_errors:
        print("Artifact verification failed:")
        for error in all_errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Artifact verification passed for {len(RUNS)} shape-named runs.")


if __name__ == "__main__":
    main()
