from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from maxwell_effect_gate.oidc_authority import validate_oidc_token_to_authority_context
from maxwell_effect_gate.policy_engine import evaluate_policy
from maxwell_effect_gate.run_demo import ARTIFACTS_DIR, run_case
from maxwell_effect_gate.verify_artifacts import verify_run

ISSUER = "https://issuer.example.test"
AUDIENCE = "maxwell-effect-gate-public-proof"
SCOPE = "change_record:create:staging"
ROLE = "change_manager"


def keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def valid_action() -> dict:
    return {
        "action_type": "create_change_control_record",
        "target_environment": "staging",
        "risk_level": "low",
        "requester_id": "requester@example.test",
        "approver_id": "approver@example.test",
        "dual_control_present": True,
    }


def valid_evidence() -> dict:
    return {
        "evidence_bundle_id": "EVID-ADV",
        "evidence_type": "simulated_cve_remediation_research",
        "source_workflow": "ai_assisted_cve_incident_research",
        "target_system": "payments-api",
        "cve_id": "CVE-2026-1043",
        "research_summary": "Synthetic public-safe adversarial case.",
        "supporting_artifacts": ["action_proposal.json"],
        "limitations": ["simulation"],
    }


def validate(token: str, public_pem: bytes):
    return validate_oidc_token_to_authority_context(
        token,
        public_pem,
        issuer=ISSUER,
        audience=AUDIENCE,
        required_scope=SCOPE,
        required_roles=[ROLE],
    )


def test_alg_none_token_fails_closed() -> None:
    _, public_pem = keypair()
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": "attacker@example.test",
            "exp": now + timedelta(minutes=15),
            "iat": now,
            "scope": SCOPE,
            "roles": [ROLE],
        },
        key="",
        algorithm="none",
    )
    result = validate(token, public_pem)
    decision = evaluate_policy(valid_action(), valid_evidence(), result.authority_context)
    assert result.valid is False
    assert decision.decision.downstream_effect_allowed is False


def test_scope_substring_confusion_fails_closed() -> None:
    private_pem, public_pem = keypair()
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": "attacker@example.test",
            "exp": now + timedelta(minutes=15),
            "iat": now,
            "scope": "change_record:create:staging-extra",
            "roles": [ROLE],
        },
        private_pem,
        algorithm="RS256",
    )
    result = validate(token, public_pem)
    decision = evaluate_policy(valid_action(), valid_evidence(), result.authority_context)
    assert result.valid is False
    assert "OIDC_REQUIRED_SCOPE_MISSING" in result.reason_codes
    assert decision.decision.downstream_effect_allowed is False


def test_manifest_hash_then_mutate_attack_fails_verification() -> None:
    run_case("staging_low_risk_dual_control")
    run_dir = ARTIFACTS_DIR / "staging_low_risk_dual_control_run"
    effect_path = run_dir / "effect_record.json"
    text = effect_path.read_text(encoding="utf-8")
    effect_path.write_text(text.replace('"status": "created"', '"status": "tampered_effect"'), encoding="utf-8")
    errors = verify_run("staging_low_risk_dual_control_run")
    assert any("hash mismatch for effect_record.json" in error for error in errors)
