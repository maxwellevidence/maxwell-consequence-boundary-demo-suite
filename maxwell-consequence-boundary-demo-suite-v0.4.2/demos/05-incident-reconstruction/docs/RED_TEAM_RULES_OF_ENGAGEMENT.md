# Red-Team Rules of Engagement — Demo 05

Demo: Maxwell Incident Reconstruction Demo

Threat class: Audit reconstruction / tamper detection

## Win condition

An attacker wins this public demo if a hostile input causes `effect_record.json` to be created without the evidence, authority, scope, policy, and required review/security/due-process conditions stated in `THREAT_MODEL.md` and `DEMO_SPEC.yml`.

An attacker also wins if the demo verifier treats a tampered committed effect as trusted.

## In scope

- Synthetic public demo inputs under `examples/demo_inputs/` and `examples/adversarial_inputs/`.
- Local CLI execution.
- Public verifier behavior.
- Public artifact boundaries: `effect_record.json` versus `NO_EFFECT_CREATED.txt`.

## Out of scope

- Production deployments.
- External systems.
- Real customer, payment, identity, regulated, or government records.
- Non-public Maxwell implementation details.

## Current status

The v0.4.0 pass is an internal adversarial harness pass. It is not an independent third-party red-team certification.
