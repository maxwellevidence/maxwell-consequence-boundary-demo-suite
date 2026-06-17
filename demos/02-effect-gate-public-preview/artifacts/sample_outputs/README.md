# Sample Artifacts

This folder contains reviewed sample outputs from the Maxwell Effect Gate public proof.

The run folder names describe input shape, not expected outcome. Inspect each decision_receipt.json for the derived decision and matched policy rule.

The samples are public-safe. They do not disclose Maxwell's private authority model, evaluator chains, scoring rules, thresholds, internal authority logic, internal evidence machinery, or production enforcement logic.

## Core invariant

```text
Only a policy-derived allow creates effect_record.json.
pause and block do not create effect_record.json.
Every run emits a repo-anchored signed manifest over generated JSON/YAML artifacts.
```
