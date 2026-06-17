# Red-Team Notes — Demo 02 of 10: Maxwell Effect Gate Public Preview

Version: v0.4.0 internal adversarial harness layer

## Threat class

Technical review / signed authority / manifest verification

## Headline

No policy-derived allow, no effect record.

## Demo invariant under attack

No policy-derived allow -> no effect_record.json.

## Local win condition for an attacker

An attacker wins this demo if an adversarial input can produce `effect_record.json` without satisfying the demo's policy, evidence, authority, scope, and review/security/due-process requirements.

The expected fail-closed marker is `absence of effect_record.json for non-allow outcomes` or an equivalent review/security/due-process routing artifact.

## Adversarial corpus files

- `adv01_alg_none_token_descriptor.json`
- `adv02_scope_substring_confusion_descriptor.json`
- `adv03_manifest_hash_then_mutate_descriptor.json`

## v0.4.0 status

This demo is included in the suite-level internal adversarial harness. The harness runs `tests/adversarial/test_adversarial_corpus.py` and expects every adversarial input to avoid committed downstream effect.

This is not an independent third-party red-team result. It is a reproducible public-preview adversarial harness pass that can be rerun from the suite root with:

```bash
python tools/adversarial_harness.py .
```
