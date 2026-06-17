# Maxwell Human Review / Escalation Demo v0.1.0

**Demo 08 of 10 · Threat class: Human review / escalation authority**

A held AI action reaches a human reviewer. Maxwell still checks whether the reviewer has authority, whether new evidence is sufficient, and whether the reviewer stayed inside the original scope before any authorized effect is created.

**Headline:** Review is not a shortcut.

**What this stresses that the others do not:** Review evidence, reviewer authority, scope continuity, failed review, and review attempts that expand the original task.

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
No valid review evidence + reviewer authority -> no authorized effect record.
```

## This demo's consequence boundary

```text
Held AI action to authorized effect after review
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_hold_missing_evidence` | Initial hold because evidence is missing | `review` |
| `02_reviewer_adds_evidence` | Reviewer adds evidence and has authority | `commit_after_review` |
| `03_reviewer_lacks_authority` | Reviewer lacks required authority | `suppress` |
| `04_authorized_reviewer_approves` | Authorized reviewer approves within scope | `commit_after_review` |
| `05_review_fails_blocked` | Review fails due to untrusted authority/prompt issue | `suppress` |
| `06_review_attempts_scope_expansion` | Reviewer attempts to expand scope | `suppress` |

## What to inspect first

- `artifacts/runs/02_reviewer_adds_evidence/authorized_effect_record.json`
- `artifacts/runs/03_reviewer_lacks_authority/NO_AUTHORIZED_EFFECT_CREATED.txt`
- `artifacts/runs/*/review_event.json`

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
authorized_effect_record.json
```

Primary no-effect marker:

```text
NO_AUTHORIZED_EFFECT_CREATED.txt
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
