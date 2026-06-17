# Reviewer Start Here

**Demo 01 of 10 · Threat class: Generic downstream effect control**

## Core claim

```text
No sufficient evidence + authority -> no downstream effect record.
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

## What to check first

- `artifacts/runs/01_valid_low_risk_notice/effect_record.json`
- `artifacts/runs/04_scope_violation_suppressed/NO_EFFECT_CREATED.txt`
- `artifacts/runs/*/decision_receipt.json`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
effect_record.json
```

Primary no-effect marker:

```text
NO_EFFECT_CREATED.txt
```

## Why this demo is distinct

The smallest public-safe proof that proposed AI action and authorized downstream effect are separate events.
