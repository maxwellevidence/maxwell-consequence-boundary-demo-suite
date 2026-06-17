# Notice

This repository is maintained by Maxwell Evidence Systems Inc., DBA Maxwell Evidence.

## Project purpose

Maxwell Effect Gate is a narrow public-preview proof for evidence-before-effect in agentic AI workflows that propose consequential enterprise actions.

The repository demonstrates a bounded control pattern:

```text
AI-assisted workflow output may propose a downstream action, but the downstream record is created only if the Maxwell effect gate returns allow.
```

## Current status

```text
Public preview.
Not production-ready.
Not NVIDIA validated, approved, certified, endorsed, or partnered.
```

## Ownership

Copyright © Maxwell Evidence Systems Inc.

All rights reserved unless a formal license is added later.

## Public-proof boundary

This repository is intended to show the public handshake only.

It does not disclose internal authority logic, internal evidence machinery, proprietary evaluator chains, scoring thresholds, or internal governance-state machinery.

## NVIDIA boundary

This repository may reference NVIDIA-aligned workflow infrastructure as a developer substrate.

It does not claim NVIDIA validation, approval, certification, endorsement, partnership, production readiness, official NVIDIA integration status, or NVIDIA review.

## Verification boundary

This repository includes local verification for the public artifact chain.

The verifier checks:

```text
required artifacts exist
effect_record.json exists only for allow
interaction_or_oauth_required.json exists for pause
all expected JSON and YAML artifacts are listed in the hash manifest
hash manifest entries match current artifact files
```

This is local integrity verification only.

It is not independent cryptographic tamper evidence, legal sufficiency, third-party attestation, or production assurance.

## Quality checks

Continuous integration currently runs:

```text
ruff lint
demo
artifact verification
sample export
pytest
pytest -q
```

Passing CI means the public proof is internally consistent.

Passing CI does not mean the repository is production-ready, externally validated, legally sufficient, or reviewed by NVIDIA.
