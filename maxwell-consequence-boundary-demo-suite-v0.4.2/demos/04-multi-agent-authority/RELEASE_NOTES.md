# Release notes update — v0.3.3 adversarial starter layer

            - Added formal THREAT_MODEL.md with the public fail-closed invariant.
            - Added examples/adversarial_inputs/ starter corpus.
            - Added tests/adversarial/ coverage asserting hostile inputs do not create downstream effect artifacts.
            - Updated package checker to canonical-public-package-checker-v0.3.3.

            # Release Notes

## v0.1.0

Initial public-preview release of the Maxwell Multi-Agent Authority Demo.

Includes:

- Six synthetic multi-agent handoff cases.
- Delegation-chain evaluation.
- Evidence-continuity checks.
- Scope and target-system boundary checks.
- Review routing and effect suppression artifacts.
- Manifest and verification report generation.
- Tests for the main invariant: task handoff is not authority handoff.

## Narrative/spec polish v0.3.2

- Standardized `DEMO_SPEC.yml` to schema `maxwell-demo-spec-v0.3.2`.
- Reworked the README head into a differentiated threat story while preserving the shared suite invariant.
- Updated the canonical package checker to validate DEMO_SPEC fields and README narrative fragments.



## v0.4.0 public-suite adversarial harness layer

- Added `make adversarial`.
- Added per-demo red-team rules of engagement.
- Added per-demo adversarial-test report.
- Integrated with the suite-level internal adversarial harness.
