# GitHub Launch Candidate Checklist

This checklist is for the v0.4.0 public GitHub release candidate of the Maxwell Consequence Boundary Demo Suite.

## Required before public push

- [x] Ten demos are present under `demos/01-*` through `demos/10-*`.
- [x] Every demo has a standardized `DEMO_SPEC.yml`.
- [x] Every demo has a differentiated README head and shared suite invariant.
- [x] Every demo includes `THREAT_MODEL.md` and adversarial-review notes.
- [x] Every demo includes an adversarial corpus under `examples/adversarial_inputs/`.
- [x] Every demo includes `make adversarial`.
- [x] Every demo includes `make package-check` using the canonical checker.
- [x] Suite-level spec check validates complete `01` through `10` coverage.
- [x] Suite-level internal adversarial harness exists and runs.
- [x] Demo 02 includes flagship fuzz and bounded mutation-smoke harnesses.

## Still not claimed

This release candidate does not claim production readiness, legal certification, independent third-party red-team validation, or full disclosure of private Maxwell internals.

## Suggested GitHub release description

`v0.4.0` is the first launch-candidate package of the Maxwell Consequence Boundary Demo Suite. It adds a formal red-team rules-of-engagement document, suite-level adversarial harness, adversarial-test report, per-demo adversarial reports, and a complete release-candidate checklist.


## v0.4.2 public links polish

- Website link present: https://www.maxwellevidence.com/
- YouTube link present: https://www.youtube.com/@MaxwellEvidence
- Links are informational and do not affect local demo execution.
