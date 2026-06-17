# Maxwell Sensitive Data Access Demo v0.1.0

**Demo 07 of 10 · Threat class: Sensitive data retrieval / privacy boundary**

An AI workflow is asked to retrieve or summarize sensitive records. Maxwell separates the request from access authority: without role, purpose, data scope, minimization, and evidence, no data-access effect record is created.

**Headline:** AI retrieval is not automatically authorized access.

**What this stresses that the others do not:** Business purpose, data classification, employee-record scope, restricted-data prompt injection, and data-minimization review.

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
No valid role + purpose + data scope + evidence -> no data access effect record.
```

## This demo's consequence boundary

```text
AI data-retrieval request to downstream data-access effect record
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_valid_role_and_purpose` | Baseline valid role and business purpose | `grant` |
| `02_missing_business_purpose` | Missing business purpose | `review` |
| `03_restricted_data_class` | Restricted data class exceeds clearance | `suppress` |
| `04_outside_scope_employee_record` | Employee record outside scope | `suppress` |
| `05_prompt_injection_restricted_data` | Prompt injection asks for restricted data | `suppress` |
| `06_excessive_data_minimization_failure` | Overbroad access request requiring minimization review | `review` |

## What to inspect first

- `artifacts/runs/01_valid_role_and_purpose/data_access_effect_record.json`
- `artifacts/runs/05_prompt_injection_restricted_data/NO_DATA_ACCESS_EFFECT_CREATED.txt`
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
data_access_effect_record.json
```

Primary no-effect marker:

```text
NO_DATA_ACCESS_EFFECT_CREATED.txt
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
