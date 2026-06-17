"""Signed-token OIDC validation tests for the public authority seam."""

from datetime import datetime, timedelta, timezone

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from maxwell_effect_gate.oidc_authority import validate_oidc_token_to_authority_context
from maxwell_effect_gate.policy_engine import evaluate_policy

ISSUER = "https://issuer.example.test"
AUDIENCE = "maxwell-effect-gate-public-proof"
SCOPE = "change_record:create:staging"
ROLE = "change_manager"


def valid_action(**overrides):
    action = {
        "action_type": "create_change_control_record",
        "target_environment": "staging",
        "risk_level": "low",
        "requester_id": "requester@example.test",
        "approver_id": "approver@example.test",
        "dual_control_present": True,
    }
    action.update(overrides)
    return action


def valid_evidence(**overrides):
    evidence = {
        "evidence_bundle_id": "EVID-001",
        "evidence_type": "simulated_cve_remediation_research",
        "source_workflow": "ai_assisted_cve_incident_research",
        "target_system": "payments-api",
        "cve_id": "CVE-2026-1043",
        "research_summary": "Simulated public-safe remediation research.",
        "supporting_artifacts": ["action_proposal.json"],
        "limitations": ["simulation"],
    }
    evidence.update(overrides)
    return evidence


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


def make_token(private_pem, **claims):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=15)
    base_claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "requester@example.test",
        "exp": exp,
        "iat": now,
        "scope": SCOPE,
        "roles": [ROLE],
    }
    base_claims.update(claims)
    return jwt.encode(base_claims, private_pem, algorithm="RS256")


def test_signed_oidc_token_maps_to_authority_context_and_allows():
    private_pem, public_pem = keypair()
    token = make_token(private_pem)

    result = validate_oidc_token_to_authority_context(
        token,
        public_pem,
        issuer=ISSUER,
        audience=AUDIENCE,
        required_scope=SCOPE,
        required_roles=[ROLE],
    )

    assert result.valid is True
    assert result.authority_context["oauth_status"] == "complete"
    assert result.authority_context["issuer"] == ISSUER
    assert result.authority_context["audience"] == AUDIENCE
    assert result.authority_context["expires_at"] != "2099-01-01T00:00:00Z"
    assert result.authority_context["expires_at"].endswith("Z")

    decision = evaluate_policy(valid_action(), valid_evidence(), result.authority_context)
    assert decision.decision.decision == "allow"


def test_invalid_audience_token_fails_closed():
    private_pem, public_pem = keypair()
    token = make_token(private_pem, aud="wrong-audience")

    result = validate_oidc_token_to_authority_context(
        token,
        public_pem,
        issuer=ISSUER,
        audience=AUDIENCE,
        required_scope=SCOPE,
        required_roles=[ROLE],
    )

    assert result.valid is False
    assert result.authority_context["oauth_status"] == "invalid"
    assert result.authority_context["token_claims_bound"] is False
    assert "OIDC_TOKEN_VALIDATION_FAILED" in result.reason_codes

    decision = evaluate_policy(valid_action(), valid_evidence(), result.authority_context)
    assert decision.decision.decision == "block"
    assert decision.decision.downstream_effect_allowed is False


def test_missing_scope_token_fails_closed():
    private_pem, public_pem = keypair()
    token = make_token(private_pem, scope="read:only")

    result = validate_oidc_token_to_authority_context(
        token,
        public_pem,
        issuer=ISSUER,
        audience=AUDIENCE,
        required_scope=SCOPE,
        required_roles=[ROLE],
    )

    assert result.valid is False
    assert "OIDC_REQUIRED_SCOPE_MISSING" in result.reason_codes

    decision = evaluate_policy(valid_action(), valid_evidence(), result.authority_context)
    assert decision.decision.decision == "block"
    assert decision.decision.downstream_effect_allowed is False


def test_missing_role_token_fails_closed():
    private_pem, public_pem = keypair()
    token = make_token(private_pem, roles=["viewer"])

    result = validate_oidc_token_to_authority_context(
        token,
        public_pem,
        issuer=ISSUER,
        audience=AUDIENCE,
        required_scope=SCOPE,
        required_roles=[ROLE],
    )

    assert result.valid is False
    assert "OIDC_REQUIRED_ROLE_MISSING" in result.reason_codes

    decision = evaluate_policy(valid_action(), valid_evidence(), result.authority_context)
    assert decision.decision.decision == "block"
    assert decision.decision.downstream_effect_allowed is False
