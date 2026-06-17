# Decoy Fail-Open Regression Proof

This directory records the v0.4.1 decoy-branch proof. A temporary copy of Demo 02 is patched so pause/block decisions incorrectly emit `effect_record.json`. The targeted tests must fail on that patched copy and pass on the unmodified copy.

This is not an external audit. It proves the shipped harness catches one known fail-open regression class.
