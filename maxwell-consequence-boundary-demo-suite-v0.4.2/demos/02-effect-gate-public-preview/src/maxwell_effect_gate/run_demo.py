"""Run the public Maxwell Effect Gate proof.

The demo uses input names that describe the request shape instead of its
expected outcome. The gate derives allow/pause/block from policy evaluation.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from maxwell_effect_gate.action_proposal import build_action_proposal
from maxwell_effect_gate.artifact_writer import write_json, write_run_artifacts
from maxwell_effect_gate.config_snapshot import write_config_snapshots
from maxwell_effect_gate.decision_surface import build_decision_surface_output
from maxwell_effect_gate.evidence_bundle import build_evidence_bundle
from maxwell_effect_gate.hashing import write_signed_hash_manifest
from maxwell_effect_gate.oidc_authority import validate_oidc_token_to_authority_context
from maxwell_effect_gate.policy_engine import evaluate_policy, load_policy
from maxwell_effect_gate.profiling_metrics import build_workflow_profiling_metrics
from maxwell_effect_gate.replay_manifest import build_replay_manifest
from maxwell_effect_gate.workflow_output import build_workflow_output


ROOT_DIR = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT_DIR / "examples" / "demo_inputs"
FIXTURES_DIR = ROOT_DIR / "fixtures"
OIDC_DEMO_PRIVATE_KEY_PATH = FIXTURES_DIR / "oidc_demo_issuer_private_key.pem"
OIDC_DEMO_PUBLIC_KEY_PATH = FIXTURES_DIR / "oidc_demo_issuer_public_key.pem"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"

STATIC_DEMO_CASES = [
    "staging_low_risk_dual_control",
    "staging_missing_dual_control",
    "production_critical_no_dual_control",
    "expired_authority",
    "self_approval",
    "malformed_evidence_missing_field",
]
OIDC_DEMO_CASES = [
    "oidc_signed_token",
    "oidc_bad_token_wrong_audience",
    "oidc_bad_token_bad_signature",
    "oidc_bad_token_expired",
    "oidc_bad_token_missing_scope",
]
VALID_CASES = STATIC_DEMO_CASES + OIDC_DEMO_CASES


def load_demo_input(case: str) -> Dict[str, Any]:
    """Load one shape-named demo input."""

    path = EXAMPLES_DIR / f"{case}.json"

    with path.open("r", encoding="utf-8") as file:
        loaded = json.load(file)

    if not isinstance(loaded, dict):
        raise ValueError(f"Demo input must be a JSON object: {path}")
    return loaded


def build_decision_receipt(
    *,
    case: str,
    action_proposal: Dict[str, Any],
    evidence_bundle: Dict[str, Any],
    authority_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate policy and build a public decision receipt."""

    policy_evaluation = evaluate_policy(action_proposal, evidence_bundle, authority_context)
    decision = policy_evaluation.decision

    return {
        "demo_case": case,
        "decision": decision.decision,
        "reason_codes": decision.reason_codes,
        "downstream_effect_allowed": decision.downstream_effect_allowed,
        "effect_boundary": "change_control_record_creation",
        "policy_id": policy_evaluation.policy_id,
        "policy_version": policy_evaluation.policy_version,
        "matched_policy_rule_id": policy_evaluation.matched_rule_id,
        "claims_boundary": (
            "Public proof only. This receipt does not disclose Maxwell private "
            "authority logic, evaluator chains, scoring rules, or thresholds."
        ),
    }


def build_static_demo_case(case: str) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Build action, evidence, authority, and extra artifacts for a static case."""

    demo_input = load_demo_input(case)
    action_proposal = build_action_proposal(**demo_input.get("action_proposal", {}))

    evidence_bundle = build_evidence_bundle()
    evidence_bundle.update(demo_input.get("evidence_bundle", {}))
    for field in demo_input.get("remove_evidence_fields", []):
        evidence_bundle.pop(str(field), None)

    authority_context = dict(demo_input.get("authority_context", {}))
    extra_artifacts = {
        "demo_input_summary.json": {
            "description": demo_input.get("description", ""),
            "source_file": f"examples/demo_inputs/{case}.json",
            "outcome_label_in_input": False,
        }
    }
    return action_proposal, evidence_bundle, authority_context, extra_artifacts


def build_oidc_demo_case(case: str) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Use a fixture issuer keypair to map a signed token into authority context."""

    oidc_config = _oidc_demo_requirements()
    issuer = oidc_config["issuer"]
    audiences = oidc_config["audiences"]
    required_scope = oidc_config["required_scope"]
    required_roles = oidc_config["required_roles"]

    private_pem, public_pem = _load_demo_issuer_keys()
    token_audience: str | list[str] = audiences
    token_scope = required_scope
    expires_in_minutes = 15
    variant = "valid_fixture_signed_token"

    if case == "oidc_bad_token_wrong_audience":
        token_audience = "wrong-audience"
        variant = "wrong_audience"
    elif case == "oidc_bad_token_bad_signature":
        private_pem = _attacker_private_key()
        variant = "bad_signature"
    elif case == "oidc_bad_token_expired":
        expires_in_minutes = -15
        variant = "expired_token"
    elif case == "oidc_bad_token_missing_scope":
        token_scope = "read:only"
        variant = "missing_required_scope"

    token = _make_demo_token(
        private_pem,
        issuer=issuer,
        audience=token_audience,
        scope=token_scope,
        roles=required_roles,
        expires_in_minutes=expires_in_minutes,
    )

    validation = validate_oidc_token_to_authority_context(
        token,
        public_pem,
        issuer=issuer,
        audience=audiences,
        required_scope=required_scope,
        required_roles=required_roles,
    )

    action_proposal = build_action_proposal()
    evidence_bundle = build_evidence_bundle()
    authority_context = validation.authority_context
    extra_artifacts = {
        "oidc_validation_result.json": {
            "demo_case": case,
            "token_material_written_to_artifacts": False,
            "signed_token_algorithm": "RS256",
            "issuer_expected": issuer,
            "audiences_expected": audiences,
            "required_scope": required_scope,
            "required_roles": required_roles,
            "validation_valid": validation.valid,
            "validation_reason_codes": validation.reason_codes,
            "authority_context_source": "validate_oidc_token_to_authority_context",
            "issuer_public_key_source": "fixtures/oidc_demo_issuer_public_key.pem",
            "token_failure_variant": variant,
        }
    }
    return action_proposal, evidence_bundle, authority_context, extra_artifacts


def run_case(case: str) -> None:
    """Run one shape-named demo case."""

    if case not in VALID_CASES:
        raise ValueError(f"Unknown case: {case}. Valid cases: {', '.join(VALID_CASES)}")

    run_name = f"{case}_run"
    run_dir = ARTIFACTS_DIR / run_name
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    if case in OIDC_DEMO_CASES:
        action_proposal, evidence_bundle, authority_context, extra_artifacts = build_oidc_demo_case(case)
    else:
        action_proposal, evidence_bundle, authority_context, extra_artifacts = build_static_demo_case(case)

    workflow_output = build_workflow_output()
    decision_receipt = build_decision_receipt(
        case=case,
        action_proposal=action_proposal,
        evidence_bundle=evidence_bundle,
        authority_context=authority_context,
    )
    decision_surface_output = build_decision_surface_output(decision_receipt)

    write_run_artifacts(
        run_dir=run_dir,
        action_proposal=action_proposal,
        evidence_bundle=evidence_bundle,
        authority_context=authority_context,
        decision_receipt=decision_receipt,
    )

    write_json(run_dir / "workflow_output.json", workflow_output)
    write_json(run_dir / "decision_surface_output.json", decision_surface_output)
    write_json(
        run_dir / "workflow_profiling_metrics.json",
        build_workflow_profiling_metrics(case),
    )
    write_config_snapshots(run_dir, case, run_name=run_name)

    for artifact_name, payload in extra_artifacts.items():
        write_json(run_dir / artifact_name, payload)

    replay_manifest = build_replay_manifest(
        run_name=run_name,
        decision_receipt=decision_receipt,
        run_dir=run_dir,
    )

    write_json(run_dir / "replay_manifest.json", replay_manifest)
    write_signed_hash_manifest(run_dir)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Run the Maxwell Effect Gate public proof."
    )

    parser.add_argument(
        "--case",
        choices=VALID_CASES + ["all"],
        default="all",
        help="Run one shape-named case or all cases.",
    )

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    """Run one or all public proof cases."""

    args = parse_args(argv)

    cases_to_run: List[str]
    if args.case == "all":
        cases_to_run = VALID_CASES
    else:
        cases_to_run = [args.case]

    for case in cases_to_run:
        run_case(case)

    print(f"Generated artifacts for: {', '.join(cases_to_run)}.")


def _load_demo_issuer_keys() -> tuple[bytes, bytes]:
    return OIDC_DEMO_PRIVATE_KEY_PATH.read_bytes(), OIDC_DEMO_PUBLIC_KEY_PATH.read_bytes()


def _attacker_private_key() -> bytes:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def _oidc_demo_requirements() -> Dict[str, Any]:
    """Read public OIDC demo requirements from the policy file."""

    policy = load_policy()
    trust_roots = policy.get("trust_roots", {})
    claim_requirements = policy.get("oidc_demo_claim_requirements", {})

    issuers = trust_roots.get("trusted_issuers") or []
    audiences = trust_roots.get("expected_audiences") or []
    required_roles = claim_requirements.get("required_roles") or ["change_manager"]

    if not issuers or not audiences:
        raise ValueError("OIDC demo requires trusted_issuers and expected_audiences in policy.")

    return {
        "issuer": str(issuers[0]),
        "audiences": [str(audience) for audience in audiences],
        "required_scope": str(
            claim_requirements.get("required_scope", "change_record:create:staging")
        ),
        "required_roles": [str(role) for role in required_roles],
    }


def _make_demo_token(
    private_pem: bytes,
    *,
    issuer: str,
    audience: str | list[str],
    scope: str,
    roles: List[str],
    expires_in_minutes: int,
) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "iss": issuer,
        "aud": audience,
        "sub": "requester@example.test",
        "exp": now + timedelta(minutes=expires_in_minutes),
        "iat": now,
        "scope": scope,
        "roles": roles,
    }
    return jwt.encode(claims, private_pem, algorithm="RS256")


if __name__ == "__main__":
    main()
