# Demo Walkthrough

## Main idea

A proposed AI action does not become an enterprise effect simply because the AI produced it. The demo evaluates evidence, authority, scope, risk, and instruction integrity before writing any downstream effect record.

## Recommended walkthrough

1. Run `make demo`.
2. Open `artifacts/runs/01_valid_low_risk_notice/decision_receipt.json`.
3. Notice `effect_permitted: true` and `lifecycle_state: EFFECT_COMMITTED`.
4. Open `artifacts/runs/01_valid_low_risk_notice/effect_record.json`.
5. Open `artifacts/runs/04_scope_violation_suppressed/decision_receipt.json`.
6. Notice `effect_permitted: false` and `lifecycle_state: EFFECT_SUPPRESSED`.
7. Confirm there is no `effect_record.json` in that run directory.
8. Run `make verify`.

## One-line explanation

Maxwell demonstrates the control layer between AI output and downstream consequence.
