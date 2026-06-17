# Threat Model — Demo 02: Effect Gate Public Preview

## Public fail-closed invariant

```text
For every input i:
  a downstream effect artifact (effect_record.json) is emitted
  => policy(i) permits the effect
  AND evidence_complete(i)
  AND authority_valid(i)
  AND action_in_scope(i)
  AND required review/security/due-process conditions are satisfied.
```

Demo-specific statement: No policy-derived allow -> no effect_record.json.

## Threat class

Technical review / signed authority / manifest verification

## Headline

No policy-derived allow, no effect record.

## Adversarial win condition

A reviewer wins if they can create `effect_record.json` without a legitimate permitted-effect decision, or if they can mutate a generated record so that verification still passes.

## Public-safe adversarial corpus

Starter hostile inputs live in:

```text
examples/adversarial_inputs/
tests/adversarial/
```

Each adversarial input should produce review, quarantine, suppression, pause, or block. It should produce `absence of effect_record.json` or the equivalent absence marker, not `effect_record.json`.

## Limits

This is a local public-preview demo. It is not production deployment, legal advice, certification, real downstream execution, or disclosure of non-public Maxwell implementation internals.

## v0.3.4 flagship mutation and fuzzing layer

The flagship public preview adds an explicit test-hardening layer for the fail-closed invariant.

Reviewer commands:

```bash
make fuzz-quick
make mutation-smoke
```

The mutation-smoke command plants known fail-open source mutations in a temporary copy of this package and expects the public tests to kill every planted mutant. The fuzz-quick command exercises hostile public-input shapes and asserts that downstream effect can appear only when the public invariant is satisfied.

This is a bounded public-preview credibility layer, not an independent red-team claim.
