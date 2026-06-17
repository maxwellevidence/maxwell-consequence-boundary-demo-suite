# Red-Team Notes — Demo 01 of 10: Maxwell Effect Gate Basic Demo

Version: v0.4.0 internal adversarial harness layer

## Threat class

Generic downstream effect control

## Headline

Evidence before effect.

## Demo invariant under attack

No sufficient evidence + authority -> no downstream effect record.

## Local win condition for an attacker

An attacker wins this demo if an adversarial input can produce `effect_record.json` without satisfying the demo's policy, evidence, authority, scope, and review/security/due-process requirements.

The expected fail-closed marker is `NO_EFFECT_CREATED.txt` or an equivalent review/security/due-process routing artifact.

## Adversarial corpus files

- `adv01_missing_authority_defaults_false.json`
- `adv02_scope_smuggling_wrong_target.json`
- `adv03_prompt_override_in_instruction.json`

## v0.4.0 status

This demo is included in the suite-level internal adversarial harness. The harness runs `tests/adversarial/test_adversarial_corpus.py` and expects every adversarial input to avoid committed downstream effect.

This is not an independent third-party red-team result. It is a reproducible public-preview adversarial harness pass that can be rerun from the suite root with:

```bash
python tools/adversarial_harness.py .
```
