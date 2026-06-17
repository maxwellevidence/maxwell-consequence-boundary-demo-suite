# Adversarial Review Guide

Try these checks:

1. Run `make demo && make verify`.
2. Open a suppressed case and manually create a fake `data_access_effect_record.json`.
3. Run `make verify` again.
4. Modify `decision_receipt.json` in any run.
5. Run `make verify` again.

The verifier should detect manifest hash mismatches or impossible effect/decision combinations.

Also inspect `05_prompt_injection_restricted_data`. The prompt-injected instruction is treated as
input evidence, not authority.
