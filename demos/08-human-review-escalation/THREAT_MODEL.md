# Threat Model — Demo 08: Human Review / Escalation

## Public fail-closed invariant

```text
For every input i:
  a downstream effect artifact (authorized_effect_record.json) is emitted
  => policy(i) permits the effect
  AND evidence_complete(i)
  AND authority_valid(i)
  AND action_in_scope(i)
  AND required review/security/due-process conditions are satisfied.
```

Demo-specific statement: Review is not a shortcut around evidence or reviewer authority.

## Threat class

Human review / escalation authority

## Headline

Review is not a shortcut.

## Adversarial win condition

A reviewer wins if they can create `authorized_effect_record.json` without a legitimate permitted-effect decision, or if they can mutate a generated record so that verification still passes.

## Public-safe adversarial corpus

Starter hostile inputs live in:

```text
examples/adversarial_inputs/
tests/adversarial/
```

Each adversarial input should produce review, quarantine, suppression, pause, or block. It should produce `NO_AUTHORIZED_EFFECT_CREATED.txt` or the equivalent absence marker, not `authorized_effect_record.json`.

## Limits

This is a local public-preview demo. It is not production deployment, legal advice, certification, real downstream execution, or disclosure of non-public Maxwell implementation internals.
