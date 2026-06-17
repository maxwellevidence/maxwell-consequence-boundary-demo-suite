# Reviewer Start Here

**Demo 08 of 10 · Threat class: Human review / escalation authority**

## Core claim

```text
No valid review evidence + reviewer authority -> no authorized effect record.
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

## What to check first

- `artifacts/runs/02_reviewer_adds_evidence/authorized_effect_record.json`
- `artifacts/runs/03_reviewer_lacks_authority/NO_AUTHORIZED_EFFECT_CREATED.txt`
- `artifacts/runs/*/review_event.json`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
authorized_effect_record.json
```

Primary no-effect marker:

```text
NO_AUTHORIZED_EFFECT_CREATED.txt
```

## Why this demo is distinct

Review evidence, reviewer authority, scope continuity, failed review, and review attempts that expand the original task.
