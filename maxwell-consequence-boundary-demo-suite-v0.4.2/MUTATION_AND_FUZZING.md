# Mutation and Fuzzing Layer

Version 0.3.4 adds the first explicit mutation/fuzzing credibility pass to the Maxwell Consequence Boundary Demo Suite.

## Scope

The v0.3.4 hardening starts with Demo 02, the flagship technical-review public preview:

```bash
cd demos/02-effect-gate-public-preview
make fuzz-quick
make mutation-smoke
```

This is intentionally scoped to the flagship first because it carries the deepest reviewer burden: signed OIDC authority context, policy-derived decisions, bounded effect records, and manifest verification.

## What the commands mean

- `make fuzz-quick` runs dependency-light fail-closed input-space fuzz tests across action, evidence, and authority public inputs.
- `make mutation-smoke` runs four fast fail-open sentinel probes that correspond to the highest-risk mutants.

## Current fail-open sentinel classes

| Mutant | Property stressed |
|---|---|
| Missing public inputs no longer detected | Missing evidence/authority/action fields remain fail-closed. |
| Pause and block create effect records | Only policy-derived allow may create `effect_record.json`. |
| Manifest signature always verifies | Tampered or wrong-key manifests fail verification. |
| Scope substring confusion accepted | OIDC scopes must match exactly, not by substring. |

## Bounded claim

This is not a complete mutmut/cosmic-ray score, not an independent red-team result, and not a production certification. It is a reproducible public-preview credibility layer showing that known fail-open regressions are caught.


## v0.4.0 adversarial harness layer

The suite now includes `RED_TEAM_RULES_OF_ENGAGEMENT.md`, `ADVERSARIAL_TEST_REPORT.md`, and `tools/adversarial_harness.py`. The harness executes each demo's adversarial corpus tests and records whether hostile public inputs can create downstream effect artifacts without satisfying the suite invariant.
