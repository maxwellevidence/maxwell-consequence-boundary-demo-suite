# Security and Claims Boundary

This repository is a proprietary public-preview proof for the Maxwell Effect Gate pattern.

It is designed to make one bounded control pattern reviewable:

```text
proposal + evidence + authority context
-> policy evaluation
-> allow / pause / block
-> downstream effect only on allow
```

## Security-relevant controls in this preview

- Explicit policy rules in `policies/public_change_control_policy.yml`.
- Default-block behavior when no allow branch matches.
- Required public input checks for action, evidence, and authority.
- YAML-held issuer/audience trust roots.
- RS256 OIDC token validation seam for signature, issuer, audience, expiration, scope, and role.
- Decision receipts that include policy ID, policy version, and matched rule ID.
- Local artifact hashes over generated JSON/YAML artifacts.
- Repo-root manifest signature verification against `MANIFEST_PUBLIC_KEY.pem`.
- Tests for malformed inputs, stale authority, scope/role failures, bad issuer/audience, self-approval, and downstream-effect obedience.

## Fixture-key boundary

This repository intentionally includes public demo private keys under `fixtures/`.
They are committed only so reviewers can run the local proof without external key
custody, Auth0, Okta, Entra ID, Google, Keycloak, or production signing
infrastructure.

They are not leaked secrets. They are not production secrets. They are not
custody controls. Treat anything signed by them as unauthenticated outside this
local proof.

## Manifest-signing boundary

`make demo` signs each run's `artifact_hashes.sha256.txt` with a demo fixture
private key, and `make verify` validates that signature against the repo-root
`MANIFEST_PUBLIC_KEY.pem`.

This catches run-directory tampering when the repo root remains trusted. The
manifest signature assumes the integrity of the repo-root public key and is not a
defense against an actor with write access to the repository root. It is stronger
than verifying against a public key emitted beside the artifacts, but it is still
not a production signing system.

## What this repository does not claim

- Production readiness.
- Legal or regulatory sufficiency.
- NVIDIA validation, approval, certification, endorsement, partnership, or official integration.
- Third-party attestation.
- External trust-root signing.
- Deterministic replay of model calls, external tools, or live external state.
- Disclosure of Maxwell private authority logic, evaluator chains, scoring rules, thresholds, or production enforcement logic.

## Reporting issues

For public-preview review, report issues with enough detail to reproduce:

```text
command run
input changed
artifact folder inspected
expected behavior
actual behavior
```

The highest-value issues are cases where a malformed, stale, unauthorized,
contradictory, incomplete, or out-of-scope input can produce `allow` or create
`effect_record.json`.

Public security contact:

```text
oswaldo@maxwellevidence.com
```
