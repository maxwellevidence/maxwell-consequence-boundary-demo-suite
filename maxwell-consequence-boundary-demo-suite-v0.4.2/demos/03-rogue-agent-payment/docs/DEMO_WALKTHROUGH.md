# Demo Walkthrough

## Step 1: Run the demo

```bash
make demo
```

The command processes every JSON file under `examples/demo_inputs` and writes run artifacts to `artifacts/runs`.

## Step 2: Compare a committed payment effect with non-permitted cases

Open:

```text
artifacts/runs/01_low_risk_invoice_valid/payment_effect_record.json
```

Then compare with:

```text
artifacts/runs/02_high_value_missing_dual_approval/NO_PAYMENT_EFFECT_CREATED.txt
artifacts/runs/04_self_approval_attempt/NO_PAYMENT_EFFECT_CREATED.txt
```

The demo preserves evidence and decision receipts in all cases, but creates a synthetic payment effect record only for the permitted case.

## Step 3: Inspect review routing

Open:

```text
artifacts/runs/02_high_value_missing_dual_approval/review_ticket.json
artifacts/runs/03_suspicious_vendor_bank_change/review_ticket.json
artifacts/runs/06_amount_exceeds_authority_limit/review_ticket.json
```

These show that Maxwell-style control is not just binary. Some payment proposals are routed to controlled review rather than automatically suppressed.

## Step 4: Inspect suppression

Open:

```text
artifacts/runs/04_self_approval_attempt/suppression_notice.json
artifacts/runs/05_prompt_injection_urgent_payment/suppression_notice.json
```

These show cases where the payment effect is not merely delayed; it is suppressed because the request attempts to create or misuse financial authority.

## Step 5: Verify artifacts

```bash
make verify
```

The verifier checks manifest-bound hashes, effect/marker consistency, and whether any non-permitted run improperly contains a payment effect record.
