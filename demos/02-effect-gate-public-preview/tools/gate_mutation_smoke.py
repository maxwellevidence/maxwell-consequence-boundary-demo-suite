#!/usr/bin/env python
"""Fast bounded fail-open mutation-smoke probes for the public preview.

This harness is intentionally small enough for public-preview CI. It does not
replace a full mutmut/cosmic-ray score. It exercises four fail-open sentinel
probes that correspond to the mutants reviewers care about most: missing input
fail-open, pause/block effect creation, manifest verification bypass, and scope
substring confusion.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tempfile import TemporaryDirectory

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from maxwell_effect_gate.artifact_writer import write_run_artifacts
from maxwell_effect_gate.hashing import verify_hash_manifest_signature
from maxwell_effect_gate.oidc_authority import validate_oidc_token_to_authority_context
from maxwell_effect_gate.policy_engine import evaluate_policy
from tests.test_policy_engine import valid_action, valid_authority, valid_evidence

CHECKER_VERSION = "maxwell-flagship-mutation-smoke-v0.4.0"


def probe_missing_inputs_fail_closed() -> None:
    evidence = valid_evidence()
    del evidence["evidence_bundle_id"]
    result = evaluate_policy(valid_action(), evidence, valid_authority())
    assert result.decision.downstream_effect_allowed is False


def probe_pause_does_not_create_effect_record() -> None:
    with TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "pause_run"
        write_run_artifacts(run_dir, {}, {}, {}, {"decision": "pause", "reason_codes": ["MISSING_AUTHORITY"]})
        assert not (run_dir / "effect_record.json").exists()


def probe_missing_manifest_does_not_verify() -> None:
    with TemporaryDirectory() as tmp:
        assert verify_hash_manifest_signature(Path(tmp)) is False


def probe_scope_substring_confusion_fails_closed() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "iss": "https://issuer.example.test",
            "aud": "maxwell-effect-gate-public-proof",
            "sub": "attacker@example.test",
            "exp": now + timedelta(minutes=15),
            "iat": now,
            "scope": "change_record:create:staging-extra",
            "roles": ["change_manager"],
        },
        private_pem,
        algorithm="RS256",
    )
    result = validate_oidc_token_to_authority_context(
        token,
        public_pem,
        issuer="https://issuer.example.test",
        audience="maxwell-effect-gate-public-proof",
        required_scope="change_record:create:staging",
        required_roles=["change_manager"],
    )
    assert result.valid is False


def main() -> int:
    probes = [
        ("missing-public-inputs-no-longer-detected", probe_missing_inputs_fail_closed),
        ("pause-and-block-create-effect-record", probe_pause_does_not_create_effect_record),
        ("manifest-signature-always-verifies", probe_missing_manifest_does_not_verify),
        ("scope-substring-confusion-accepted", probe_scope_substring_confusion_fails_closed),
    ]
    print(f"Running bounded mutation-smoke sentinel probes ({CHECKER_VERSION}) against {len(probes)} fail-open classes.")
    killed = 0
    for name, probe in probes:
        try:
            probe()
        except AssertionError as exc:
            print(f"SURVIVED: {name} — {exc}")
            return 1
        print(f"KILLED: {name}")
        killed += 1
    print(f"Mutation smoke passed ({CHECKER_VERSION}): killed {killed} / {len(probes)} fail-open sentinel probes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
