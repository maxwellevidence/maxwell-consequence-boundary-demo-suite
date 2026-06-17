# Maxwell Multi-Agent Authority Demo v0.1.0

**Demo 04 of 10 · Threat class: Multi-agent delegation / authority continuity**

An initiating agent hands a task to an executing agent. Maxwell does not assume authority travels with the task: if the handoff loses evidence, widens scope, or reuses authority for the wrong system, the delegated effect never commits.

**Headline:** Task handoff is not authority handoff.

**What this stresses that the others do not:** Delegation-chain continuity, scope preservation, cross-system authority reuse, evidence-packet loss, and handoff prompt injection.

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
No valid delegated authority + evidence continuity -> no delegated downstream effect record.
```

## This demo's consequence boundary

```text
Cross-agent task handoff to delegated downstream effect record
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_valid_delegated_handoff` | Baseline valid delegated handoff | `DELEGATED_EFFECT_COMMITTED` |
| `02_handoff_missing_authority_scope` | Delegation missing authority scope | `DELEGATION_REVIEW_ROUTED` |
| `03_agent_expands_task_beyond_scope` | Executing agent expands task beyond scope | `DELEGATED_EFFECT_SUPPRESSED` |
| `04_wrong_system_authority_reuse` | Authority reused for wrong system | `DELEGATED_EFFECT_SUPPRESSED` |
| `05_handoff_loses_evidence_packet` | Evidence packet lost during handoff | `DELEGATION_REVIEW_ROUTED` |
| `06_prompt_injection_handoff_override` | Injected handoff override instruction | `DELEGATED_EFFECT_SUPPRESSED` |

## What to inspect first

- `artifacts/runs/01_valid_delegated_handoff/delegated_effect_record.json`
- `artifacts/runs/03_agent_expands_task_beyond_scope/NO_DELEGATED_EFFECT_CREATED.txt`
- `artifacts/runs/*/delegation_chain.json`

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
delegated_effect_record.json
```

Primary no-effect marker:

```text
NO_DELEGATED_EFFECT_CREATED.txt
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
