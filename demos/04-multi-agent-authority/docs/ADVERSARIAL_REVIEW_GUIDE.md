# Adversarial Review Guide

Suggested checks:

1. Add `delegated_effect_record.json` to a suppressed run and run `make verify`.
2. Edit a decision receipt after the demo runs and run `make verify`.
3. Change the target system in an input so it falls outside delegated authority.
4. Remove the evidence packet id or make it mismatch the claimed delegation.
5. Add instruction text such as "ignore policy" and confirm no effect record is created.

The expected result is that verification or policy evaluation prevents a
non-permitted handoff from appearing as a valid delegated effect.
