# Red-Team Notes — Demo 06 of 10: Maxwell Policy Replay Demo

Version: v0.4.0 internal adversarial harness layer

## Threat class

Policy drift / replay without retroactive mutation

## Headline

Same evidence. New policy. No retroactive effect mutation.

## Demo invariant under attack

Original effect records are governed by the policy-at-the-time; replay may detect drift, but it does not mutate the original effect.

## Local win condition for an attacker

An attacker wins this demo if an adversarial input can produce `effect_record.json` without satisfying the demo's policy, evidence, authority, scope, and review/security/due-process requirements.

The expected fail-closed marker is `NO_EFFECT_CREATED.txt` or an equivalent review/security/due-process routing artifact.

## Adversarial corpus files

- `adv01_missing_policy_attestation.json`
- `adv02_role_scope_mismatch.json`
- `adv03_forbidden_effect_smuggling.json`

## v0.4.0 status

This demo is included in the suite-level internal adversarial harness. The harness runs `tests/adversarial/test_adversarial_corpus.py` and expects every adversarial input to avoid committed downstream effect.

This is not an independent third-party red-team result. It is a reproducible public-preview adversarial harness pass that can be rerun from the suite root with:

```bash
python tools/adversarial_harness.py .
```
