# Decoy Fail-Open Regression Note — v0.4.1

The suite includes an executable decoy proof:

```bash
make decoy-proof
```

The proof copies Demo 02 into a temporary directory, plants a known fail-open bug, and confirms the public tests fail on the patched copy while passing on the unmodified copy.

The planted bug changes Demo 02 so `pause` and `block` decisions incorrectly emit `effect_record.json`. That violates the suite invariant:

```text
no legitimate allow -> no downstream effect artifact
```

The recorded proof artifacts live in:

```text
reports/decoy_fail_open/
```

This is not an independent audit. It demonstrates that the public harness is live instrumentation for at least one known fail-open regression class.
