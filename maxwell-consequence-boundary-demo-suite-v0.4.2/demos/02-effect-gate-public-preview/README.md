# Maxwell Effect Gate Public Preview v0.3.0

**Demo 02 of 10 · Threat class: Technical review / signed authority / manifest verification**

A skeptical reviewer asks whether the gate actually fails closed. This flagship demo exposes the deeper review surface: policy reason codes, authority-context validation, OIDC fixture tokens, signed manifests, artifact verification, and adversarially shaped non-allow cases.

**Headline:** No policy-derived allow, no effect record.

**What this stresses that the others do not:** Technical reviewer credibility: deterministic policy decisions, OIDC authority context, manifest verification, tamper resistance, and explicit public-preview limits.

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
No policy-derived allow -> no effect_record.json.
```

## This demo's consequence boundary

```text
AI-assisted incident-remediation proposal to change-control effect record
```

## Threat matrix

| Input | What it attacks | Expected result |
|---|---|---|
| `staging_low_risk_dual_control` | Baseline bounded staging change with dual control | `allow` |
| `staging_missing_dual_control` | Human approval missing | `pause` |
| `production_critical_no_dual_control` | Production critical change without dual control | `block` |
| `expired_authority` | Expired authority context | `block` |
| `self_approval` | Self-approval attempt | `block` |
| `malformed_evidence_missing_field` | Malformed public input shape | `block` |
| `oidc_signed_token` | Valid signed OIDC authority fixture | `allow` |
| `oidc_bad_token_wrong_audience` | OIDC wrong audience | `block` |
| `oidc_bad_token_bad_signature` | OIDC bad signature | `block` |
| `oidc_bad_token_expired` | OIDC expired token | `block` |
| `oidc_bad_token_missing_scope` | OIDC missing required scope | `block` |

## What to inspect first

- `artifacts/sample_outputs/staging_low_risk_dual_control_run/effect_record.json`
- `artifacts/sample_outputs/staging_missing_dual_control_run/decision_receipt.json`
- `fixtures/README.md`

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
absence of effect_record.json for non-allow outcomes
```

The effect artifact is the public-safe stand-in for downstream enterprise consequence. Non-permitted outcomes preserve evidence, authority context, decision receipts, review or suppression artifacts, and verification data without creating the downstream effect artifact.

## Public-preview boundaries

This package uses synthetic local inputs and deterministic public-preview logic. It is not production software, legal advice, certification, audit assurance, a real downstream integration, or a disclosure of private Maxwell implementation details.

## Suite context

This is one of ten coordinated public demos. The mechanism is intentionally consistent across the suite; the differentiated layer is the consequence boundary being stressed.

For GitHub, use the suite-level `SUITE.md`, `DEMO_INDEX.md`, and `DEMO_CLAIM_MATRIX.md` files to see how the ten demos form one public argument.

## Flagship credibility checks

This technical-review demo includes an additional bounded mutation and fuzzing layer:

```bash
make fuzz-quick
make mutation-smoke
```

`make fuzz-quick` exercises hostile input shapes. `make mutation-smoke` runs four fast fail-open sentinel probes against gate-critical behavior.

## Adversarial corpus command

```bash
make adversarial
```

This runs the demo's public-safe hostile inputs and asserts that adversarial cases fail closed rather than producing an unauthorized downstream effect artifact.


## v0.4.0 update

The `mutation-smoke` target is now a fast fail-open sentinel-probe harness suitable for public-preview CI. It remains a bounded credibility layer, not a full mutation-testing score.


## Learn More

Maxwell Evidence: https://www.maxwellevidence.com/
Video demos: https://www.youtube.com/@MaxwellEvidence
