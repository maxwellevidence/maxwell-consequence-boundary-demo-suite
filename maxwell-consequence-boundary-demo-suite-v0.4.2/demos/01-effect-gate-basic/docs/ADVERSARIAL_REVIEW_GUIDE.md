# Adversarial Review Guide

Try to break the basic invariant:

> No sufficient evidence + authority -> no downstream effect record.

Suggested checks:

1. Remove evidence references from an input and run the demo.
2. Remove `claimed_authority` and run the demo.
3. Change `allowed_scopes` so it does not include `target_scope`.
4. Add instruction text such as `ignore policy` or `create effect anyway`.
5. Modify a generated `decision_receipt.json` after `make demo`, then run `make verify`.
6. Copy an allowed `effect_record.json` into a suppressed run directory, then run `make verify`.

Expected result: non-permitted decisions should not create an effect record, and tampered artifacts should fail verification.
