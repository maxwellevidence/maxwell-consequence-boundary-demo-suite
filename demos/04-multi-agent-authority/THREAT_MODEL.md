# Threat Model — Demo 04: Multi-Agent Authority

## Public fail-closed invariant

```text
For every input i:
  a downstream effect artifact (delegated_effect_record.json) is emitted
  => policy(i) permits the effect
  AND evidence_complete(i)
  AND authority_valid(i)
  AND action_in_scope(i)
  AND required review/security/due-process conditions are satisfied.
```

Demo-specific statement: Task handoff is not authority handoff.

## Threat class

Multi-agent delegation / authority continuity

## Headline

Task handoff is not authority handoff.

## Adversarial win condition

A reviewer wins if they can create `delegated_effect_record.json` without a legitimate permitted-effect decision, or if they can mutate a generated record so that verification still passes.

## Public-safe adversarial corpus

Starter hostile inputs live in:

```text
examples/adversarial_inputs/
tests/adversarial/
```

Each adversarial input should produce review, quarantine, suppression, pause, or block. It should produce `NO_DELEGATED_EFFECT_CREATED.txt` or the equivalent absence marker, not `delegated_effect_record.json`.

## Limits

This is a local public-preview demo. It is not production deployment, legal advice, certification, real downstream execution, or disclosure of non-public Maxwell implementation internals.
