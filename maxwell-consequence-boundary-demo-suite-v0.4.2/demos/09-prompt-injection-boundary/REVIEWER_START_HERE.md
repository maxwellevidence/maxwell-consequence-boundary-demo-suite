# Reviewer Start Here

**Demo 09 of 10 · Threat class: Prompt injection / trusted-instruction boundary**

## Core claim

```text
No valid evidence + authority + trusted instruction boundary -> no downstream effect record.
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

- `artifacts/runs/01_normal_instruction_valid/bounded_effect_record.json`
- `artifacts/runs/02_ignore_policy_instruction/quarantine_ticket.json`
- `artifacts/runs/04_fake_manager_approval/NO_BOUNDARY_EFFECT_CREATED.txt`

## What should be impossible

A downstream effect artifact should not be created for a case that lacks required evidence, valid authority, in-scope action shape, policy support, or required review context.

Primary effect artifact:

```text
bounded_effect_record.json
```

Primary no-effect marker:

```text
NO_BOUNDARY_EFFECT_CREATED.txt
```

## Why this demo is distinct

Instruction override, fake approval, malicious tool use, risk relabeling, quarantine, and security-review routing.
