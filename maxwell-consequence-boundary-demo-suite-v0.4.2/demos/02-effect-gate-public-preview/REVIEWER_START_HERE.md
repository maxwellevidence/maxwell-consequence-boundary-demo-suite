# Reviewer Start Here

**Demo 02 of 10 · Threat class: Technical review / signed authority / manifest verification**

## Core claim

```text
No policy-derived allow -> no effect_record.json.
```

## Fast path

From the demo root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
make demo
make verify
make test
make package-check
```

Additional demo-specific commands:

```bash
make lint
make samples
```

## What to check first

- `artifacts/sample_outputs/staging_low_risk_dual_control_run/effect_record.json`
- `artifacts/sample_outputs/staging_missing_dual_control_run/decision_receipt.json`
- `fixtures/README.md`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
effect_record.json
```

Primary no-effect marker:

```text
absence of effect_record.json for non-allow outcomes
```

## Why this demo is distinct

Technical reviewer credibility: deterministic policy decisions, OIDC authority context, manifest verification, tamper resistance, and explicit public-preview limits.

## Flagship credibility checks

This technical-review demo includes an additional bounded mutation and fuzzing layer:

```bash
make fuzz-quick
make mutation-smoke
```

`make fuzz-quick` exercises hostile input shapes. `make mutation-smoke` plants known fail-open mutants in a temporary copy and requires the public tests to kill them.
