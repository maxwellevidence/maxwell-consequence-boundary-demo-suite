# Release notes update — v0.3.3 adversarial starter layer

            - Added formal THREAT_MODEL.md with the public fail-closed invariant.
            - Added examples/adversarial_inputs/ starter corpus.
            - Added tests/adversarial/ coverage asserting hostile inputs do not create downstream effect artifacts.
            - Updated package checker to canonical-public-package-checker-v0.3.3.

            # Release Notes

## v0.1.0

Initial public-preview release of the Maxwell Rogue Agent Payment Demo.

Includes:

- Six synthetic payment proposal cases.
- Payment evidence bundle generation.
- Payment authority context normalization.
- Payment-specific policy reason codes.
- Review ticket creation for review-routed cases.
- Suppression notice creation for unauthorized payment effects.
- Synthetic payment effect record creation only when policy permits.
- Manifest-bound verification.
- Public package hygiene tooling.

## Narrative/spec polish v0.3.2

- Standardized `DEMO_SPEC.yml` to schema `maxwell-demo-spec-v0.3.2`.
- Reworked the README head into a differentiated threat story while preserving the shared suite invariant.
- Updated the canonical package checker to validate DEMO_SPEC fields and README narrative fragments.



## v0.4.0 public-suite adversarial harness layer

- Added `make adversarial`.
- Added per-demo red-team rules of engagement.
- Added per-demo adversarial-test report.
- Integrated with the suite-level internal adversarial harness.
