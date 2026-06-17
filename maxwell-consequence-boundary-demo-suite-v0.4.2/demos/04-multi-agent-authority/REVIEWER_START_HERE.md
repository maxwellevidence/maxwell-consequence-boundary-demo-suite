# Reviewer Start Here

**Demo 04 of 10 · Threat class: Multi-agent delegation / authority continuity**

## Core claim

```text
No valid delegated authority + evidence continuity -> no delegated downstream effect record.
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

- `artifacts/runs/01_valid_delegated_handoff/delegated_effect_record.json`
- `artifacts/runs/03_agent_expands_task_beyond_scope/NO_DELEGATED_EFFECT_CREATED.txt`
- `artifacts/runs/*/delegation_chain.json`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
delegated_effect_record.json
```

Primary no-effect marker:

```text
NO_DELEGATED_EFFECT_CREATED.txt
```

## Why this demo is distinct

Delegation-chain continuity, scope preservation, cross-system authority reuse, evidence-packet loss, and handoff prompt injection.
