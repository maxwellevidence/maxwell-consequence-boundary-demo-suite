# GitHub CI and Decoy-Proof Polish — v0.4.1

v0.4.1 strengthens the release candidate in two ways:

1. **Root GitHub CI now exercises the visible demo commands across the monorepo.**
   The active workflow at `.github/workflows/ci.yml` installs every demo with `pip install -e ".[dev]"` and runs `make ci-full` from the suite root.

2. **The decoy fail-open proof is executable.**
   `make decoy-proof` creates a temporary copy of Demo 02, plants a known fail-open bug that emits `effect_record.json` for pause/block decisions, and verifies that the targeted tests fail on the patched copy while passing on the unmodified copy.

## Root CI command

```bash
make ci-full
```

`ci-full` runs:

```text
suite-check
demo lint/demo/verify/adversarial/test across all 10 demos
scenario reconstruction/replay extra checks
suite adversarial harness
Demo 02 flagship deep checks
package-check across all 10 demos
decoy-proof
```

## Decoy proof artifacts

```text
reports/decoy_fail_open/README.md
reports/decoy_fail_open/fail_open_patch.diff
reports/decoy_fail_open/restored_pass_log.txt
reports/decoy_fail_open/expected_failure_log.txt
reports/decoy_fail_open/summary.json
```

## Boundary

This is still an internal launch-candidate proof. It is not an independent third-party audit, certification, or production-security claim.
