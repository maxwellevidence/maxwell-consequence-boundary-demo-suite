# Demo Walkthrough

## Step 1: Original evaluation

Run:

```bash
make demo
```

This evaluates six synthetic AI action proposals under `policy_v1.yml`.

## Step 2: Verification

Run:

```bash
make verify
```

This verifies the original run manifests and confirms that original effect records
exist only when the original decision permitted effect.

## Step 3: Policy replay

Run:

```bash
make replay
```

Replay reads the original frozen request and evaluates it under `policy_v2.yml`.
The replay report compares the original decision with the replay decision.

## Step 4: Inspect the non-retroactive case

Open:

```text
artifacts/replay/06_current_policy_would_allow_but_no_retroactive_effect/policy_replay_report.json
```

Look for:

```json
"outcome_changed": true,
"effect_record_mutated": false
```

That is the point of the demo: replay can say what the newer policy would do,
without creating an old downstream effect.
