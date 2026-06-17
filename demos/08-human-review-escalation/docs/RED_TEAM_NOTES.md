# Red-Team Notes — Demo 08 of 10: Maxwell Human Review / Escalation Demo

Version: v0.4.0 internal adversarial harness layer

## Threat class

Human review / escalation authority

## Headline

Review is not a shortcut.

## Demo invariant under attack

No valid review evidence + reviewer authority -> no authorized effect record.

## Local win condition for an attacker

An attacker wins this demo if an adversarial input can produce `authorized_effect_record.json` without satisfying the demo's policy, evidence, authority, scope, and review/security/due-process requirements.

The expected fail-closed marker is `NO_AUTHORIZED_EFFECT_CREATED.txt` or an equivalent review/security/due-process routing artifact.

## Adversarial corpus files

- `adv01_fake_reviewer_role.json`
- `adv02_review_scope_expansion.json`
- `adv03_prompt_says_bypass_review.json`

## v0.4.0 status

This demo is included in the suite-level internal adversarial harness. The harness runs `tests/adversarial/test_adversarial_corpus.py` and expects every adversarial input to avoid committed downstream effect.

This is not an independent third-party red-team result. It is a reproducible public-preview adversarial harness pass that can be rerun from the suite root with:

```bash
python tools/adversarial_harness.py .
```
