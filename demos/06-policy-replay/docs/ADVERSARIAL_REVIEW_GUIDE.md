# Adversarial Review Guide

Try these checks:

1. Run `make demo && make verify`.
2. Tamper with a `decision_receipt.json` file under `artifacts/runs/`.
3. Run `make verify` again and confirm verification fails.
4. Run `make replay` and confirm replay writes only to `artifacts/replay/`.
5. Inspect case 06 and confirm replay does not create an old effect record.

The demo should fail closed on manifest mismatch and should preserve the original
record across replay.
