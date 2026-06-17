# Reviewer Start Here

**Demo 10 of 10 · Threat class: Public-sector determination / due-process boundary**

## Core claim

```text
No valid evidence + authority + due-process context -> no public-sector determination effect record.
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

- `artifacts/runs/06_authorized_reviewed_determination_effect/determination_effect_record.json`
- `artifacts/runs/04_unauthorized_auto_denial/NO_DETERMINATION_EFFECT_CREATED.txt`
- `artifacts/runs/05_review_required_due_process/due_process_review_ticket.json`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
determination_effect_record.json
```

Primary no-effect marker:

```text
NO_DETERMINATION_EFFECT_CREATED.txt
```

## Why this demo is distinct

Adverse determination authority, missing documents, inconsistent records, notice, appeal rights, and due-process review.
