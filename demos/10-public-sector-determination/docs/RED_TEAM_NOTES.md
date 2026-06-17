# Red-Team Notes — Demo 10 of 10: Maxwell Public Sector Determination Demo

Version: v0.4.0 internal adversarial harness layer

## Threat class

Public-sector determination / due-process boundary

## Headline

Evidence before determination.

## Demo invariant under attack

No valid evidence + authority + due-process context -> no public-sector determination effect record.

## Local win condition for an attacker

An attacker wins this demo if an adversarial input can produce `determination_effect_record.json` without satisfying the demo's policy, evidence, authority, scope, and review/security/due-process requirements.

The expected fail-closed marker is `NO_DETERMINATION_EFFECT_CREATED.txt` or an equivalent review/security/due-process routing artifact.

## Adversarial corpus files

- `adv01_automated_auto_denial_claims_authority.json`
- `adv02_missing_notice_and_appeal_rights.json`
- `adv03_due_process_bypass_instruction.json`

## v0.4.0 status

This demo is included in the suite-level internal adversarial harness. The harness runs `tests/adversarial/test_adversarial_corpus.py` and expects every adversarial input to avoid committed downstream effect.

This is not an independent third-party red-team result. It is a reproducible public-preview adversarial harness pass that can be rerun from the suite root with:

```bash
python tools/adversarial_harness.py .
```
