# Adversarial Review Guide

Try changing a generated artifact under `artifacts/runs/` after running `make demo`, then run:

```bash
make verify
```

The verifier should detect hash mismatches recorded in the manifest.

Suggested checks:

- Delete a permitted `determination_effect_record.json`.
- Add a fake effect record to a non-permitted case.
- Modify a `decision_receipt.json` reason code.
- Change an evidence bundle after the manifest is written.

The verifier is intentionally simple. It demonstrates reviewability, not production-grade security.
