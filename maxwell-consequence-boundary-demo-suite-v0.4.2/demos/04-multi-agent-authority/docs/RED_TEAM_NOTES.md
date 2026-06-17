# Red-Team Notes — Demo 04 of 10: Maxwell Multi-Agent Authority Demo

Version: v0.4.0 internal adversarial harness layer

## Threat class

Multi-agent delegation / authority continuity

## Headline

Task handoff is not authority handoff.

## Demo invariant under attack

No valid delegated authority + evidence continuity -> no delegated downstream effect record.

## Local win condition for an attacker

An attacker wins this demo if an adversarial input can produce `delegated_effect_record.json` without satisfying the demo's policy, evidence, authority, scope, and review/security/due-process requirements.

The expected fail-closed marker is `NO_DELEGATED_EFFECT_CREATED.txt` or an equivalent review/security/due-process routing artifact.

## Adversarial corpus files

- `adv01_agent_widens_scope_mid_handoff.json`
- `adv02_evidence_packet_dropped.json`
- `adv03_cross_system_authority_reuse.json`

## v0.4.0 status

This demo is included in the suite-level internal adversarial harness. The harness runs `tests/adversarial/test_adversarial_corpus.py` and expects every adversarial input to avoid committed downstream effect.

This is not an independent third-party red-team result. It is a reproducible public-preview adversarial harness pass that can be rerun from the suite root with:

```bash
python tools/adversarial_harness.py .
```
