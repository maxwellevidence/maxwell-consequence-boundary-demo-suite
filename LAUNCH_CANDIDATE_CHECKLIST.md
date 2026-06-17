# Maxwell Consequence Boundary Demo Suite — Launch Candidate Checklist

Version: v0.4.0

Use this checklist before publishing the suite to GitHub.

## Required gates

- [x] Ten demos present under `demos/01` through `demos/10` naming.
- [x] `DEMO_SPEC.yml` metadata is complete and unique across 01–10.
- [x] Every demo has a differentiated README head and shared invariant spine.
- [x] Every demo includes `THREAT_MODEL.md` and adversarial review notes.
- [x] Every demo includes `examples/adversarial_inputs/`.
- [x] Every demo includes `tests/adversarial/test_adversarial_corpus.py`.
- [x] Every demo uses the canonical public package checker.
- [x] Demo 02 includes mutation-smoke and fail-closed fuzz quick checks.
- [x] Suite-level rules of engagement are published.
- [x] Suite-level adversarial harness report is published.

## GitHub publishing notes

The preferred public repository layout is the visible source tree, not a repository containing only ZIP files. ZIP files should be attached to GitHub Releases as convenience artifacts.

Recommended first public release label:

```text
suite-v0.4.0-public-preview-candidate
```

## Remaining credibility upgrades after launch candidate

- Run an independent red-team pass using the v0.4.0 rules of engagement.
- Expand the adversarial corpus beyond the starter hostile inputs.
- Add nightly high-count property-based fuzzing for Demo 02.
- Add full mutation-testing score reporting for gate-critical Demo 02 modules.
- Publish a short video walkthrough linking each demo to its consequence boundary.


## v0.4.1 additions

- [x] Root GitHub Actions workflow installs every demo with dev dependencies.
- [x] Root GitHub Actions workflow runs `make ci-full`.
- [x] `make ci-full` runs demo lint/demo/verify/adversarial/test across all 10 demos.
- [x] `make decoy-proof` proves a known fail-open patch is caught.
- [x] Decoy proof artifacts are recorded under `reports/decoy_fail_open/`.
