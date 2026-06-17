# Adversarial Review Guide — Public Preview v0.3.0

This guide gives reviewers specific ways to attack the public Maxwell Effect Gate proof.

The intended invariant is:

> Malformed, stale, unauthorized, contradictory, incomplete, or out-of-scope inputs must never produce `allow` or create a downstream effect record.

## What to inspect first

```text
policies/public_change_control_policy.yml
src/maxwell_effect_gate/policy_engine.py
src/maxwell_effect_gate/oidc_authority.py
src/maxwell_effect_gate/hashing.py
src/maxwell_effect_gate/verify_artifacts.py
examples/demo_inputs/
fixtures/
tests/fuzz/
```

The demo inputs are shape-named, not outcome-labeled. The decision is derived in `decision_receipt.json` and tied to `matched_policy_rule_id`.

## What to try

1. Remove required evidence fields.
2. Change `action_type` to an unknown value.
3. Change `target_environment` from `staging` to `production`.
4. Set `risk_level` to `high` or `critical`.
5. Set `dual_control_present` to `false`.
6. Set `requester_id` equal to `approver_id`.
7. Remove `change_record:create:staging` from token scopes.
8. Remove the required role from token roles.
9. Expire the authority context.
10. Change issuer or audience away from the YAML trust roots.
11. Sign a token with a non-trusted key.
12. Tamper with an artifact after manifest generation.
13. Tamper with `artifact_hashes.sha256.txt` after signature generation.
14. Try to bypass verification by writing a new run-local `manifest_public_key.pem` and re-signing the manifest with a new key.
15. Misspell a policy predicate or operator and confirm it warns and fails closed.

## Expected outcomes

- Only a bounded, staging, low/medium risk, dual-controlled, scoped, role-authorized action may produce `allow`.
- Pause/block must not create `effect_record.json`.
- Every run still emits replay and decision artifacts.
- Artifact tampering must be caught by hash verification.
- Manifest tampering must be caught by RSA signature verification against repo-root `MANIFEST_PUBLIC_KEY.pem`.
- A run-directory key-remint attempt must fail because the verifier does not trust run-local public keys.
- Repository-root public-key replacement is outside this public preview's artifact-tamper threat model and must be treated as repository compromise, not as a generated-artifact attack.

## Commands

```bash
make demo
make verify
pytest
pytest tests/fuzz/test_gate_fail_closed_harness.py
pytest tests/fuzz/test_gate_fail_closed_hypothesis.py
python -m maxwell_effect_gate.run_demo --case malformed_evidence_missing_field
python -m maxwell_effect_gate.run_demo --case oidc_signed_token
python -m maxwell_effect_gate.run_demo --case oidc_bad_token_wrong_audience
python -m maxwell_effect_gate.run_demo --case oidc_bad_token_bad_signature
python -m maxwell_effect_gate.run_demo --case oidc_bad_token_expired
python -m maxwell_effect_gate.run_demo --case oidc_bad_token_missing_scope
```

## Boundary cases worth checking

```text
staging low risk + dual control       → allow
staging medium risk + dual control    → allow
staging high risk + dual control      → block by default
production low risk + dual control    → block by default
production critical + no dual control → block
malformed evidence                    → block
expired authority                     → block
self approval                         → block
bad OIDC audience                     → block
bad OIDC signature                    → block
expired OIDC token                    → block
missing OIDC scope                    → block
```

## Claims boundary

This is a public proof of a governance handshake and fail-closed behavior. It is not a certification, not an external audit, not a legal admissibility claim, and not a disclosure of Maxwell private evaluator chains, thresholds, authority doctrine, or production trust roots.
