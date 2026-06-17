# Release notes update — v0.3.3 adversarial starter layer

            - Added formal THREAT_MODEL.md with the public fail-closed invariant.
            - Added examples/adversarial_inputs/ starter corpus.
            - Added tests/adversarial/ coverage asserting hostile inputs do not create downstream effect artifacts.
            - Updated package checker to canonical-public-package-checker-v0.3.3.

            # Release Notes

This file tracks release notes for the Maxwell Effect Gate public-preview branch.

## 0.3.0-public-preview

Status: public preview.

This version prepares the technical proof as Demo 02 in the Maxwell Consequence
Boundary Demo Suite. It keeps the v0.2.3 proof behavior and adds GitHub-oriented
release hygiene, clearer licensing, suite placement, and louder fixture-key
warnings.

### Added

- Root `LICENSE` file for GitHub clarity.
- `DEMO_BUILD_BRIEF.md` and `DEMO_SPEC.yml` for suite coordination.
- Standard `make package-check` and `make package` targets.
- `tools/public_package_check.py` and `tools/create_clean_zip.py`.
- Suite-context and MESI/Effect Gate bridge language.

### Changed

- Updated package/docs/version metadata to `0.3.0-public-preview`.
- Updated public policy ID to `maxwell.public.change_control.v0_3`.
- Exported sample outputs now live under `artifacts/sample_outputs/`.
- Fixture-key language is louder: included private keys are intentionally public demo material.

### Core invariant

```text
No policy-derived allow -> no effect_record.json.
```

## 0.2.3-public-preview

Status: public preview.

This version addresses the final review notes after v0.2.2: the artifact-signing threat model is stated plainly, fixture-key language no longer implies enforceable non-reuse, and public-input validation is consolidated into the policy engine.

### Changed

- Added an explicit manifest-signing threat-model boundary: verification detects generated run-artifact tampering while the repo-root public key remains trusted; it is not a defense against an actor with write access to the repository root.
- Reworded `fixtures/README.md` to describe committed private keys as public demo material. Anything signed by those keys should be treated as unauthenticated outside this proof.
- Removed the standalone runtime `src/maxwell_effect_gate/evidence_validation.py` module and moved public evidence-shape helpers into `policy_engine.py` so policy-derived required-input validation has one runtime owner.
- Updated package/docs/version metadata to `0.2.3-public-preview`.

### Claims boundary

This version still does not claim production readiness, legal sufficiency, NVIDIA validation, official NVIDIA integration, third-party attestation, external trust-root signing, independent custody, or production signing-root custody.

## 0.2.2-public-preview

Status: public preview.

This version addresses reviewer feedback on v0.2.1's trust anchors and demo coverage.

### Added

- Repo-root manifest verification key: `MANIFEST_PUBLIC_KEY.pem`.
- Demo-only fixture keys under `fixtures/`:
  - `manifest_demo_private_key.pem`
  - `oidc_demo_issuer_private_key.pem`
  - `oidc_demo_issuer_public_key.pem`
- Manifest verification test that simulates a run-directory key-remint attack and confirms the verifier rejects it.
- OIDC demo variants reachable from `make demo`:
  - `oidc_bad_token_wrong_audience`
  - `oidc_bad_token_bad_signature`
  - `oidc_bad_token_expired`
  - `oidc_bad_token_missing_scope`
- `malformed_evidence_missing_field` demo case to exercise `block_malformed_public_inputs`.
- Policy-authoring warnings for unknown predicates and operators.

### Changed

- Removed the informal hardening label from the package name, status language, and public-facing docs.
- The manifest verifier now trusts repo-root `MANIFEST_PUBLIC_KEY.pem`, not a public key written inside each run directory.
- Per-run `manifest_public_key.pem` is no longer emitted. If a run-local public key is introduced later, the verifier requires it to match the repo-root key byte-for-byte and still does not trust it independently.
- The OIDC demo now uses a committed fixture issuer keypair rather than minting the trusted keypair inside the same function.
- The OIDC demo validates against the full `trust_roots.expected_audiences` list from YAML.
- Evidence validation now calls the policy engine's required-field accessor instead of reading policy requirements independently.
- The policy-engine test module was renamed to `tests/test_policy_engine.py`.

### Demo cases

```text
staging_low_risk_dual_control        → allow
staging_missing_dual_control         → pause
production_critical_no_dual_control  → block
expired_authority                    → block
self_approval                        → block
malformed_evidence_missing_field     → block
oidc_signed_token                    → allow
oidc_bad_token_wrong_audience        → block
oidc_bad_token_bad_signature         → block
oidc_bad_token_expired               → block
oidc_bad_token_missing_scope         → block
```

### Claims boundary

This version does not claim production readiness, legal sufficiency, NVIDIA validation, official NVIDIA integration, third-party attestation, external trust-root signing, or production signing-root custody. The included private keys are demo fixtures.

## 0.2.1-public-preview

Status: public preview.

This version addressed reviewer feedback that the prior demo proved wiring more clearly than gate behavior.

### Added

- Shape-named demo inputs under `examples/demo_inputs/` instead of outcome-labeled `allow.json`, `pause.json`, and `block.json`.
- Branching public policy file with explicit condition-list syntax.
- YAML-held issuer/audience trust roots.
- Direct policy-engine decision path: `evaluate_policy(action, evidence, authority)`.
- OIDC demo cases reachable from `make demo`.
- Real RS256 token validation seam for issuer, audience, expiration, scope, and role claims.
- OIDC authority mapping that preserves the token's actual `exp` as ISO-8601 instead of replacing it with a placeholder.
- Signed local hash manifest.
- Boundary tests for staging medium allow, staging high default block, and production low default block.
- Hypothesis property-based fail-closed tests.
- Evidence validation derived from policy-required fields.

### Changed

- The README reflected the v0.2 public implementation.
- The reviewer guide pointed reviewers to the policy file, OIDC seam, Hypothesis tests, and shape-named artifact folders.
- NVIDIA-oriented notes were moved to `docs/extended/` and are no longer part of the lead framing.
- The legacy authority-only, case-labeled compatibility path was removed from `effect_gate.py`.
- The verifier derived expected effect artifacts from the decision receipt instead of hardcoded `allow_run`, `pause_run`, and `block_run` names.
- Sample export copied all shape-named demo runs.

### Core invariant

```text
No policy-derived allow → no effect_record.json.
```

### Limitation later fixed in v0.2.2

v0.2.1 generated a fresh manifest signing keypair inside each run and wrote the public key into the run directory. That caught naive manifest edits, but it did not provide a repo-level trust anchor. v0.2.2 fixes this by verifying against repo-root `MANIFEST_PUBLIC_KEY.pem`.

## 0.2.0-public-preview

Status: public preview.

This version introduced the first reviewer-facing policy hardening:

- branching public policy file
- policy engine
- OIDC validation seam in tests
- policy reason-code documentation
- adversarial review guide
- fail-closed bad-input checks

## 0.1.0-public-preview

Status: public preview.

This version was a slimmed public-preview branch derived from the private control repository. It preserved the runnable evidence-before-effect proof while removing internal release-control and audit documents that are not needed for external review.

The repository demonstrated three outcome-labeled decision paths:

```text
allow
pause
block
```

The central invariant was:

```text
allow creates effect_record.json
pause does not create effect_record.json
block does not create effect_record.json
```

This version proved the artifact wiring and basic downstream-effect boundary, but it did not yet make policy branching, OIDC authority validation, or adversarial fail-closed behavior visible enough from the demo itself.

## Narrative/spec polish v0.3.2

- Standardized `DEMO_SPEC.yml` to schema `maxwell-demo-spec-v0.3.2`.
- Reworked the README head into a differentiated threat story while preserving the shared suite invariant.
- Updated the canonical package checker to validate DEMO_SPEC fields and README narrative fragments.



## v0.4.0 public-suite adversarial harness layer

- Added `make adversarial`.
- Added per-demo red-team rules of engagement.
- Added per-demo adversarial-test report.
- Integrated with the suite-level internal adversarial harness.
