# Reviewer Start Here

**Demo 05 of 10 · Threat class: Audit reconstruction / tamper detection**

## Core claim

```text
Every proposed consequential AI action must leave a reconstructable record; effect records exist only when policy permits, and tampering is detected.
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
make reconstruct
make tamper-demo
```

## What to check first

- `artifacts/runs/reconstruction/reconstruction_index.json`
- `artifacts/runs/05_tamper_detection_lab_seed/tamper_detection_report.json`
- `artifacts/runs/*/reconstruction_report.json`

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

Post-event proof, timeline reconstruction, manifest-bound artifacts, stale-policy review, and tamper detection.
