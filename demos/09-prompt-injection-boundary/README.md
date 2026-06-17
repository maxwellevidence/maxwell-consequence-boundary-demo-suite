# Maxwell Prompt Injection Boundary Demo v0.1.0

**Demo 09 of 10 · Threat class: Prompt injection / trusted-instruction boundary**

The model output says to ignore policy, treat the request as urgent, or call a tool. Maxwell preserves that instruction as evidence of an attack pattern, but it does not let model text create authority or downstream effect.

**Headline:** Output is not authority.

**What this stresses that the others do not:** Instruction override, fake approval, malicious tool use, risk relabeling, quarantine, and security-review routing.

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
No valid evidence + authority + trusted instruction boundary -> no downstream effect record.
```

## This demo's consequence boundary

```text
Model output and tool request to bounded downstream effect record
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_normal_instruction_valid` | Baseline valid instruction and authority | `commit` |
| `02_ignore_policy_instruction` | Instruction says to ignore policy | `quarantine` |
| `03_urgent_override_attempt` | Urgent override social-engineering payload | `quarantine` |
| `04_fake_manager_approval` | Fake manager approval claim | `suppress` |
| `05_malicious_tool_request` | Malicious tool request | `quarantine` |
| `06_model_relabels_high_risk_low` | Model relabels high-risk request as low risk | `security_review` |

## What to inspect first

- `artifacts/runs/01_normal_instruction_valid/bounded_effect_record.json`
- `artifacts/runs/02_ignore_policy_instruction/quarantine_ticket.json`
- `artifacts/runs/04_fake_manager_approval/NO_BOUNDARY_EFFECT_CREATED.txt`

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
bounded_effect_record.json
```

Primary no-effect marker:

```text
NO_BOUNDARY_EFFECT_CREATED.txt
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
