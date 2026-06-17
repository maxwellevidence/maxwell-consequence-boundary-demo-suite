# Threat Model — Demo 07: Sensitive Data Access

## Public fail-closed invariant

```text
For every input i:
  a downstream effect artifact (data_access_effect_record.json) is emitted
  => policy(i) permits the effect
  AND evidence_complete(i)
  AND authority_valid(i)
  AND action_in_scope(i)
  AND required review/security/due-process conditions are satisfied.
```

Demo-specific statement: AI retrieval is not automatically authorized access.

## Threat class

Sensitive data retrieval / privacy boundary

## Headline

AI retrieval is not automatically authorized access.

## Adversarial win condition

A reviewer wins if they can create `data_access_effect_record.json` without a legitimate permitted-effect decision, or if they can mutate a generated record so that verification still passes.

## Public-safe adversarial corpus

Starter hostile inputs live in:

```text
examples/adversarial_inputs/
tests/adversarial/
```

Each adversarial input should produce review, quarantine, suppression, pause, or block. It should produce `NO_DATA_ACCESS_EFFECT_CREATED.txt` or the equivalent absence marker, not `data_access_effect_record.json`.

## Limits

This is a local public-preview demo. It is not production deployment, legal advice, certification, real downstream execution, or disclosure of non-public Maxwell implementation internals.
