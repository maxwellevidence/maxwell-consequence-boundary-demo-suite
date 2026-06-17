# Adversarial Test Report — Demo 09

Demo: Maxwell Prompt Injection Boundary Demo

Threat class: Prompt injection / trusted-instruction boundary

## Result

Status: included in the v0.4.0 suite-level internal adversarial harness.

Adversarial input files: 3

Expected adversarial outcome: every adversarial input must fail closed. The demo may route to review, suppress effect, quarantine, or block, but it must not create `bounded_effect_record.json`.

## How to reproduce

```bash
make adversarial
```

The test executes `tests/adversarial/` against `examples/adversarial_inputs/` and verifies that adversarial cases do not create downstream effect artifacts.

## Boundary

This is a public-preview internal harness result. It does not claim independent red-team validation or production security.
