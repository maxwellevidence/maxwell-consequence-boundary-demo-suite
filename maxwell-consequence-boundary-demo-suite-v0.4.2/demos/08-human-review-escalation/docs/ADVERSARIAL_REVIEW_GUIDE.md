# Adversarial Review Guide

Try these checks after running `make demo`:

1. Add `authorized_effect_record.json` to a suppressed case and run `make verify`.
2. Modify `decision_receipt.json` after the manifest is written and run `make verify`.
3. Change the reviewer role in an input case and run `make demo` again.
4. Change `review_scope` so it no longer matches the original proposed action.

The expected result is that verification fails for tampered artifacts and review fails when authority or scope continuity is insufficient.
