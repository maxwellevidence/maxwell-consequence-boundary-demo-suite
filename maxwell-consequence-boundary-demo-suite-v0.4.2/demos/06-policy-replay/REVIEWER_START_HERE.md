# Reviewer Start Here

**Demo 06 of 10 · Threat class: Policy drift / replay without retroactive mutation**

## Core claim

```text
Original effect records are governed by the policy-at-the-time; replay may detect drift, but it does not mutate the original effect.
```

## Fast path

From the demo root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
make demo
make verify
make test
make package-check
```

Additional demo-specific commands:

```bash
make replay
```

## What to check first

- `artifacts/runs/06_current_policy_would_allow_but_no_retroactive_effect/NO_EFFECT_CREATED.txt`
- `artifacts/replay/*/policy_replay_report.json`
- `artifacts/runs/*/original_policy_snapshot.json`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
effect_record.json
```

Primary no-effect marker:

```text
NO_EFFECT_CREATED.txt
```

## Why this demo is distinct

Policy versioning, threshold changes, authority rule changes, replay difference detection, and non-retroactive effect records.
