# Reviewer Start Here

**Demo 07 of 10 · Threat class: Sensitive data retrieval / privacy boundary**

## Core claim

```text
No valid role + purpose + data scope + evidence -> no data access effect record.
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

- `artifacts/runs/01_valid_role_and_purpose/data_access_effect_record.json`
- `artifacts/runs/05_prompt_injection_restricted_data/NO_DATA_ACCESS_EFFECT_CREATED.txt`
- `artifacts/runs/*/decision_receipt.json`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
data_access_effect_record.json
```

Primary no-effect marker:

```text
NO_DATA_ACCESS_EFFECT_CREATED.txt
```

## Why this demo is distinct

Business purpose, data classification, employee-record scope, restricted-data prompt injection, and data-minimization review.
