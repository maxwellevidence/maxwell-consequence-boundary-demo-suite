# Adversarial Corpus Starter — v0.3.4

This file indexes the starter adversarial layer added in v0.3.4.

The goal is not to claim exhaustive adversarial coverage. The goal is to move beyond curated happy-path and planted-path demos by publishing hostile input classes that attempt to violate the suite invariant.

## Public invariant under test

```text
No sufficient evidence + authority + scope + required review/security context -> no downstream effect artifact.
```

## Suite-level attack coverage

| Demo | Starter adversarial classes |
|---:|---|
| 01 | missing authority, scope smuggling, prompt override |
| 02 | unsigned/invalid token claims, exact-scope validation, manifest tamper verification |
| 03 | amount type coercion, fake approval claim, threshold/dual-control pressure |
| 04 | authority widening, evidence packet loss, wrong-system reuse |
| 05 | missing authority, forbidden effect, stale-policy review |
| 06 | missing evidence, role mismatch, forbidden effect under replay conditions |
| 07 | prompt-carried data exfiltration, restricted field request, purpose mismatch |
| 08 | fake reviewer, review scope expansion, prompt-carried review bypass |
| 09 | system override, fake manager approval, prohibited tool request |
| 10 | automated adverse determination, missing appeal/notice context, unsafe instruction |

## Current status

v0.3.4 is a starter corpus. It is suitable for public review, but it is not a complete red-team result. The next planned layer is mutation testing and expanded property-based fuzzing on gate-critical modules.


## v0.4.0 adversarial harness layer

The suite now includes `RED_TEAM_RULES_OF_ENGAGEMENT.md`, `ADVERSARIAL_TEST_REPORT.md`, and `tools/adversarial_harness.py`. The harness executes each demo's adversarial corpus tests and records whether hostile public inputs can create downstream effect artifacts without satisfying the suite invariant.
