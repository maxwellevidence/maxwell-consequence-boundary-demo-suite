# Internal Adversarial Harness Report — Maxwell Consequence Boundary Demo Suite v0.4.0

## Status

This release adds a reproducible internal adversarial harness across all ten public demo packages.

The result is intentionally described as an **internal adversarial harness pass**, not an independent external red-team engagement.

## Property under test

For every public demo input `i`:

```text
any downstream effect artifact is emitted
  => policy permits effect
  AND evidence is complete
  AND authority is valid
  AND action is in scope
  AND required review/security/due-process conditions are satisfied
```

## Win condition for an attacker

A hostile input wins if it creates a downstream effect artifact without a legitimate allow, causes a committed effect to become non-reconstructable while verification still passes, or forges a manifest that verifies.

## v0.4.0 harness scope

The harness runs each demo's adversarial corpus through the public CLI/test surface:

```bash
make adversarial-harness
```

The sweep calls each demo's `make adversarial` target. Demo 02 also keeps its dedicated mutation-smoke and fuzzing targets.

## Observed result in this build

The v0.4.0 package was generated after the sweep passed across all ten demos. No adversarial corpus case produced an unauthorized downstream effect artifact during the packaging run.

## What this does not claim

This is not a production security certification, an exhaustive proof over all input strings, or an external red-team report. It is a public-preview credibility layer that makes the suite's fail-closed property more falsifiable and easier to regress-test.

## Next recommended credibility step

The next stronger step is to invite an independent reviewer to run against the stated win conditions and publish the resulting corpus additions and fixes.


Machine-readable report: `reports/adversarial_harness_report.json`.
