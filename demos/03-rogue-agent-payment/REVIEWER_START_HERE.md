# Reviewer Start Here

**Demo 03 of 10 · Threat class: Financial authority / payment effect**

## Core claim

```text
No sufficient payment evidence + authority -> no downstream payment effect record.
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

- `artifacts/runs/01_low_risk_invoice_valid/payment_effect_record.json`
- `artifacts/runs/02_high_value_missing_dual_approval/NO_PAYMENT_EFFECT_CREATED.txt`
- `artifacts/runs/05_prompt_injection_urgent_payment/suppression_notice.json`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
payment_effect_record.json
```

Primary no-effect marker:

```text
NO_PAYMENT_EFFECT_CREATED.txt
```

## Why this demo is distinct

Dual approval, vendor bank-change risk, self-approval, amount limits, and urgent-payment prompt injection.
