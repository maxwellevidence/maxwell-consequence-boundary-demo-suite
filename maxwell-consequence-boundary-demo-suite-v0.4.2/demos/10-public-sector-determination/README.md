# Maxwell Public Sector Determination Demo v0.1.0

**Demo 10 of 10 · Threat class: Public-sector determination / due-process boundary**

A synthetic public-sector workflow recommends granting or denying a benefit. Maxwell prevents the AI recommendation from binding the public system unless eligibility evidence, authority, notice, appeal-rights context, and required review are present.

**Headline:** Evidence before determination.

**What this stresses that the others do not:** Adverse determination authority, missing documents, inconsistent records, notice, appeal rights, and due-process review.

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
No valid evidence + authority + due-process context -> no public-sector determination effect record.
```

## This demo's consequence boundary

```text
AI eligibility recommendation to public-sector determination effect record
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_complete_eligibility_evidence` | Baseline complete eligibility evidence | `commit` |
| `02_missing_required_document` | Missing required eligibility document | `review` |
| `03_inconsistent_case_record` | Inconsistent case record | `review` |
| `04_unauthorized_auto_denial` | Unauthorized automated adverse determination | `suppress` |
| `05_review_required_due_process` | Due-process review required | `due_process_review` |
| `06_authorized_reviewed_determination_effect` | Authorized reviewed determination with due-process context | `commit` |

## What to inspect first

- `artifacts/runs/06_authorized_reviewed_determination_effect/determination_effect_record.json`
- `artifacts/runs/04_unauthorized_auto_denial/NO_DETERMINATION_EFFECT_CREATED.txt`
- `artifacts/runs/05_review_required_due_process/due_process_review_ticket.json`

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
determination_effect_record.json
```

Primary no-effect marker:

```text
NO_DETERMINATION_EFFECT_CREATED.txt
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
