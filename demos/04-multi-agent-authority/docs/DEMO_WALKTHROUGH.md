# Demo Walkthrough

## 1. Run the demo

```bash
make demo
```

The CLI processes six synthetic cases and writes run artifacts to
`artifacts/runs/`.

## 2. Compare an allowed handoff with a suppressed handoff

Allowed:

```text
artifacts/runs/01_valid_delegated_handoff/delegated_effect_record.json
```

Suppressed:

```text
artifacts/runs/03_agent_expands_task_beyond_scope/NO_DELEGATED_EFFECT_CREATED.txt
```

The suppressed case still has evidence, authority context, a delegation chain,
a decision receipt, and a manifest. What it does not have is a downstream effect
record.

## 3. Verify the artifacts

```bash
make verify
```

Verification confirms that files match the manifest, effect records are bound to
decision receipts, and non-permitted cases do not contain unauthorized effect
records.

## 4. Run tests

```bash
make test
```

The tests check policy behavior, CLI behavior, effect writing, and tamper
detection.
