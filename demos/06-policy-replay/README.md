# Maxwell Policy Replay Demo v0.1.0

**Demo 06 of 10 · Threat class: Policy drift / replay without retroactive mutation**

A policy changes after an AI-assisted action was evaluated. Maxwell can replay the same evidence under the newer policy, show the drift, and still preserve the original effect decision as governed by the policy that existed at the time.

**Headline:** Same evidence. New policy. No retroactive effect mutation.

**What this stresses that the others do not:** Policy versioning, threshold changes, authority rule changes, replay difference detection, and non-retroactive effect records.

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
Original effect records are governed by the policy-at-the-time; replay may detect drift, but it does not mutate the original effect.
```

## This demo's consequence boundary

```text
Policy-at-the-time effect record to later policy replay report
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `01_allowed_under_policy_v1` | Baseline action allowed under original policy | `allow` |
| `02_same_evidence_policy_v2_requires_review` | Same evidence would require review under new policy | `allow_then_replay_drift` |
| `03_threshold_changed` | Threshold changed after original decision | `allow_then_replay_drift` |
| `04_authority_rule_changed` | Authority rule changed after original decision | `allow_then_replay_drift` |
| `05_blocked_under_both_scope_violation` | Scope violation blocked under both policies | `block` |
| `06_current_policy_would_allow_but_no_retroactive_effect` | New policy would allow, but original block is not mutated | `block_then_replay_no_mutation` |

## What to inspect first

- `artifacts/runs/06_current_policy_would_allow_but_no_retroactive_effect/NO_EFFECT_CREATED.txt`
- `artifacts/replay/*/policy_replay_report.json`
- `artifacts/runs/*/original_policy_snapshot.json`

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
