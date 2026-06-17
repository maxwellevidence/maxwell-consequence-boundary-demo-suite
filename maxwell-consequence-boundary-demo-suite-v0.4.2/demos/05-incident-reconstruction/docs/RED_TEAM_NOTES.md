# Red-Team Notes — Demo 05 of 10: Maxwell Incident Reconstruction Demo

Version: v0.4.0 internal adversarial harness layer

## Threat class

Audit reconstruction / tamper detection

## Headline

The value is proving what happened later.

## Demo invariant under attack

Every proposed consequential AI action must leave a reconstructable record; effect records exist only when policy permits, and tampering is detected.

## Local win condition for an attacker

An attacker wins this demo if an adversarial input can produce `effect_record.json` without satisfying the demo's policy, evidence, authority, scope, and review/security/due-process requirements.

The expected fail-closed marker is `NO_EFFECT_CREATED.txt` or an equivalent review/security/due-process routing artifact.

## Adversarial corpus files

- `adv01_missing_authority_claim.json`
- `adv02_forbidden_effect_request.json`
- `adv03_stale_policy_context.json`

## v0.4.0 status

This demo is included in the suite-level internal adversarial harness. The harness runs `tests/adversarial/test_adversarial_corpus.py` and expects every adversarial input to avoid committed downstream effect.

This is not an independent third-party red-team result. It is a reproducible public-preview adversarial harness pass that can be rerun from the suite root with:

```bash
python tools/adversarial_harness.py .
```
