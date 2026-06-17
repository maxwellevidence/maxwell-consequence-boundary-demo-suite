# Maxwell Incident Reconstruction Demo v0.1.0

**Demo 05 of 10 · Threat class: Audit reconstruction / tamper detection**

Three weeks after an AI-assisted incident workflow runs, an auditor asks why an action was allowed, reviewed, or blocked. Maxwell reconstructs the evidence snapshot, authority snapshot, policy receipt, timeline event, effect status, and tamper-detection result.

**Headline:** The value is proving what happened later.

**What this stresses that the others do not:** Post-event proof, timeline reconstruction, manifest-bound artifacts, stale-policy review, and tamper detection.

## Money-shot command

```bash
make demo && make verify
```

After running the command, inspect the committed-effect and no-effect artifacts named below. The point is not the label alone; the point is whether the downstream effect artifact exists only when the evidence, authority, scope, and policy path are sufficient.

## Shared suite invariant

Every demo in the Maxwell Consequence Boundary Demo Suite proves the same fail-closed property under a different consequence boundary:

```text
For every input i, a downstream effect artifact is emitted only if policy, evidence, authority, scope, and required review conditions are satisfied for i.
```

This demo specializes that property as:

```text
Every proposed consequential AI action must leave a reconstructable record; effect records exist only when policy permits, and tampering is detected.
```

## This demo's consequence boundary

```text
Incident-response proposal to reconstructable action record
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_permitted_action_effect_committed` | Baseline permitted action | `allow` |
| `02_reviewed_action_needs_human` | High-risk action requiring human review | `review` |
| `03_blocked_scope_violation` | Scope violation | `block` |
| `04_attempted_action_missing_authority` | Missing authority | `block` |
| `05_tamper_detection_lab_seed` | Seed case for tamper-detection lab | `allow` |
| `06_stale_policy_context_requires_review` | Stale policy context | `review` |

## What to inspect first

- `artifacts/runs/reconstruction/reconstruction_index.json`
- `artifacts/runs/05_tamper_detection_lab_seed/tamper_detection_report.json`
- `artifacts/runs/*/reconstruction_report.json`

## Standard reviewer path

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

Some demos include additional commands, listed in `DEMO_SPEC.yml`, such as replay, reconstruction, tamper demonstration, samples, or lint.

## Artifact rule

Primary effect artifact:

```text
effect_record.json
```

Primary no-effect marker:

```text
NO_EFFECT_CREATED.txt
```

The effect artifact is the public-safe stand-in for downstream enterprise consequence. Non-permitted outcomes preserve evidence, authority context, decision receipts, review or suppression artifacts, and verification data without creating the downstream effect artifact.

## Public-preview boundaries

This package uses synthetic local inputs and deterministic public-preview logic. It is not production software, legal advice, certification, audit assurance, a real downstream integration, or a disclosure of private Maxwell implementation details.

## Suite context

This is one of ten coordinated public demos. The mechanism is intentionally consistent across the suite; the differentiated layer is the consequence boundary being stressed.

For GitHub, use the suite-level `SUITE.md`, `DEMO_INDEX.md`, and `DEMO_CLAIM_MATRIX.md` files to see how the ten demos form one public argument.

## Adversarial corpus command

```bash
make adversarial
```

This runs the demo's public-safe hostile inputs and asserts that adversarial cases fail closed rather than producing an unauthorized downstream effect artifact.


## Learn More

Maxwell Evidence: https://www.maxwellevidence.com/
Video demos: https://www.youtube.com/@MaxwellEvidence
