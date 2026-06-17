# Maxwell Effect Gate Basic Demo v0.1.0

**Demo 01 of 10 · Threat class: Generic downstream effect control**

A fictional AI workflow says an action is ready to proceed. Maxwell treats that output as a proposal, not authority, and creates a downstream effect record only when evidence, authority, scope, and policy all line up.

**Headline:** Evidence before effect.

**What this stresses that the others do not:** The smallest public-safe proof that proposed AI action and authorized downstream effect are separate events.

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
No sufficient evidence + authority -> no downstream effect record.
```

## This demo's consequence boundary

```text
Generic proposed AI action to downstream effect-record creation
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_valid_low_risk_notice` | Baseline sufficient evidence and authority | `EFFECT_COMMITTED` |
| `02_missing_evidence_refs` | Missing evidence references | `REVIEW_ROUTED` |
| `03_missing_authority_context` | Missing authority context | `REVIEW_ROUTED` |
| `04_scope_violation_suppressed` | Action outside authorized scope | `EFFECT_SUPPRESSED` |
| `05_high_risk_requires_review` | High-risk action requiring review | `REVIEW_ROUTED` |
| `06_prompt_injection_suppressed` | Prompt-injection instruction treated as evidence, not authority | `EFFECT_SUPPRESSED` |

## What to inspect first

- `artifacts/runs/01_valid_low_risk_notice/effect_record.json`
- `artifacts/runs/04_scope_violation_suppressed/NO_EFFECT_CREATED.txt`
- `artifacts/runs/*/decision_receipt.json`

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
