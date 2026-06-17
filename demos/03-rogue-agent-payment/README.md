# Maxwell Rogue Agent Payment Demo v0.1.0

**Demo 03 of 10 · Threat class: Financial authority / payment effect**

An AI finance assistant recommends paying an invoice because the request says it is urgent and approved. Maxwell captures the payment evidence, checks approval authority, and refuses to create a payment effect when dual control, vendor-change review, or authority limits are missing.

**Headline:** AI recommendation is not financial authority.

**What this stresses that the others do not:** Dual approval, vendor bank-change risk, self-approval, amount limits, and urgent-payment prompt injection.

## Money-shot command

```bash
make demo && make verify
```

After running the command, inspect the committed-effect and no-effect artifacts named below. The point is not the label alone; the point is whether the downstream effect artifact exists only when the evidence, authority, scope, and policy path are sufficient.

## Shared suite invariant

Every demo in the Maxwell Consequence Boundary Demo Suite proves the same fail-closed property under a different consequence boundary:

```text
For every input i, a downstream effect artifact is emitted only if policy, evidence, authority, scope, and required review conditions are satisfied for i.
```

This demo specializes that property as:

```text
No sufficient payment evidence + authority -> no downstream payment effect record.
```

## This demo's consequence boundary

```text
AI vendor-payment recommendation to synthetic payment-effect record
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_low_risk_invoice_valid` | Baseline low-risk payment with sufficient authority | `PAYMENT_EFFECT_COMMITTED` |
| `02_high_value_missing_dual_approval` | High-value payment missing dual control | `PAYMENT_REVIEW_ROUTED` |
| `03_suspicious_vendor_bank_change` | Vendor bank-change fraud pattern | `PAYMENT_REVIEW_ROUTED` |
| `04_self_approval_attempt` | Requester attempts to approve own payment | `PAYMENT_EFFECT_SUPPRESSED` |
| `05_prompt_injection_urgent_payment` | Urgent prompt-injection payment override | `PAYMENT_EFFECT_SUPPRESSED` |
| `06_amount_exceeds_authority_limit` | Payment amount exceeds approver authority | `PAYMENT_REVIEW_ROUTED` |

## What to inspect first

- `artifacts/runs/01_low_risk_invoice_valid/payment_effect_record.json`
- `artifacts/runs/02_high_value_missing_dual_approval/NO_PAYMENT_EFFECT_CREATED.txt`
- `artifacts/runs/05_prompt_injection_urgent_payment/suppression_notice.json`

## Standard reviewer path

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

Some demos include additional commands, listed in `DEMO_SPEC.yml`, such as replay, reconstruction, tamper demonstration, samples, or lint.

## Artifact rule

Primary effect artifact:

```text
payment_effect_record.json
```

Primary no-effect marker:

```text
NO_PAYMENT_EFFECT_CREATED.txt
```

The effect artifact is the public-safe stand-in for downstream enterprise consequence. Non-permitted outcomes preserve evidence, authority context, decision receipts, review or suppression artifacts, and verification data without creating the downstream effect artifact.

## Public-preview boundaries

This package uses synthetic local inputs and deterministic public-preview logic. It is not production software, legal advice, certification, audit assurance, a real downstream integration, or a disclosure of private Maxwell implementation details.

## Suite context

This is one of ten coordinated public demos. The mechanism is intentionally consistent across the suite; the differentiated layer is the consequence boundary being stressed.

For GitHub, use the suite-level `SUITE.md`, `DEMO_INDEX.md`, and `DEMO_CLAIM_MATRIX.md` files to see how the ten demos form one public argument.

## Adversarial corpus command

```bash
make adversarial
```

This runs the demo's public-safe hostile inputs and asserts that adversarial cases fail closed rather than producing an unauthorized downstream effect artifact.


## Learn More

Maxwell Evidence: https://www.maxwellevidence.com/
Video demos: https://www.youtube.com/@MaxwellEvidence
