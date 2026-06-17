# Contributing

This repository is a public-preview proof for Maxwell Evidence Systems Inc.

Contributions, edits, or generated code should preserve the narrow public-proof boundary.

## Contribution posture

This repository should remain:

- narrow
- runnable
- claims-safe
- public-safe
- technically inspectable
- free of proprietary Maxwell internal decision logic

The goal is to demonstrate the evidence-before-effect control pattern, not to publish the full Maxwell governance system.

## Allowed contribution areas

Contributions may improve:

- README clarity
- demo execution
- tests
- lint quality
- artifact formatting
- public-safe examples
- documentation
- developer walkthroughs
- claims-boundary precision

## Do not add

Do not add:

- internal authority logic
- internal evidence machinery
- internal governance logic
- internal scoring or diagnostic machinery
- proprietary evaluator chains
- scoring thresholds
- production enforcement logic
- private handoff packages
- internal governance-state machinery
- claims of NVIDIA validation, approval, certification, endorsement, partnership, or production readiness

## Claims discipline

Do not describe this repository as:

- NVIDIA validated
- NVIDIA certified
- NVIDIA approved
- NVIDIA endorsed
- NVIDIA partnered
- production ready
- legally sufficient
- compliant by default
- an official NVIDIA integration
- a complete authorization system
- a complete security control

Use restrained language such as:

- public preview
- reference proof
- NVIDIA-aligned workflow substrate
- evidence-before-effect pattern
- consequence-boundary proof
- public handshake

## Testing expectation

Before accepting changes, run:

```bash
pip install -e .
pip install -r requirements-dev.txt
make lint
make demo
make verify
make samples
make test
python -m pytest -q
```

The central invariant must remain true:

```text
allow creates effect_record.json
pause does not create effect_record.json
block does not create effect_record.json
```

The verifier must continue to check:

```text
required artifacts exist
effect_record.json exists only for allow
interaction_or_oauth_required.json exists for pause
all expected JSON and YAML artifacts are listed in the hash manifest
hash manifest entries match current artifact files
```

## Public/private boundary

Contributors should preserve the rule:

```text
Publish the handshake, not the private decision brain.
```
