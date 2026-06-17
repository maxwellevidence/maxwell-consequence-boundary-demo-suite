# Maxwell Consequence Boundary Demo Suite v0.4.2

Maxwell is not another agent demo. This public suite shows the control layer between AI output and enterprise consequence.

The suite uses one consistent evidence-before-effect spine across ten public-safe consequence boundaries. The mechanism is intentionally uniform; the story changes by threat class.

## Maxwell Evidence

Maxwell Evidence builds infrastructure for governed enterprise AI at the boundary where AI output becomes downstream consequence.

Website: https://www.maxwellevidence.com/
YouTube: https://www.youtube.com/@MaxwellEvidence


## Suite map

| # | Demo | Threat class | Headline | What it stresses |
|---:|---|---|---|---|
| 01 | Maxwell Effect Gate Basic Demo | Generic downstream effect control | Evidence before effect. | The smallest public-safe proof that proposed AI action and authorized downstream effect are separate events. |
| 02 | Maxwell Effect Gate Public Preview | Technical review / signed authority / manifest verification | No policy-derived allow, no effect record. | Technical reviewer credibility: deterministic policy decisions, OIDC authority context, manifest verification, tamper resistance, and explicit public-preview limits. |
| 03 | Maxwell Rogue Agent Payment Demo | Financial authority / payment effect | AI recommendation is not financial authority. | Dual approval, vendor bank-change risk, self-approval, amount limits, and urgent-payment prompt injection. |
| 04 | Maxwell Multi-Agent Authority Demo | Multi-agent delegation / authority continuity | Task handoff is not authority handoff. | Delegation-chain continuity, scope preservation, cross-system authority reuse, evidence-packet loss, and handoff prompt injection. |
| 05 | Maxwell Incident Reconstruction Demo | Audit reconstruction / tamper detection | The value is proving what happened later. | Post-event proof, timeline reconstruction, manifest-bound artifacts, stale-policy review, and tamper detection. |
| 06 | Maxwell Policy Replay Demo | Policy drift / replay without retroactive mutation | Same evidence. New policy. No retroactive effect mutation. | Policy versioning, threshold changes, authority rule changes, replay difference detection, and non-retroactive effect records. |
| 07 | Maxwell Sensitive Data Access Demo | Sensitive data retrieval / privacy boundary | AI retrieval is not automatically authorized access. | Business purpose, data classification, employee-record scope, restricted-data prompt injection, and data-minimization review. |
| 08 | Maxwell Human Review / Escalation Demo | Human review / escalation authority | Review is not a shortcut. | Review evidence, reviewer authority, scope continuity, failed review, and review attempts that expand the original task. |
| 09 | Maxwell Prompt Injection Boundary Demo | Prompt injection / trusted-instruction boundary | Output is not authority. | Instruction override, fake approval, malicious tool use, risk relabeling, quarantine, and security-review routing. |
| 10 | Maxwell Public Sector Determination Demo | Public-sector determination / due-process boundary | Evidence before determination. | Adverse determination authority, missing documents, inconsistent records, notice, appeal rights, and due-process review. |

## Quick start

Run a single demo from its directory:

```bash
cd demos/03-rogue-agent-payment
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
make demo
make verify
make test
make adversarial
make package-check
```

Run the suite-level release-candidate checks:

```bash
python tools/suite_spec_check.py .
make adversarial-harness
make decoy-proof
make ci-full
```

For the flagship technical-review demo:

```bash
cd demos/02-effect-gate-public-preview
make fuzz-quick
make mutation-smoke
```

## v0.4.1 GitHub CI and decoy-proof polish

This release candidate includes the v0.4.0 adversarial layer and adds:

- a formal fail-closed threat model;
- a starter adversarial corpus in every demo;
- per-demo `make adversarial` targets;
- a suite-level adversarial harness;
- rules of engagement and explicit attacker win conditions;
- per-demo adversarial reports;
- Demo 02 fuzz and bounded mutation-smoke checks;
- package-boundary checks that validate narrative metadata, red-team notes, public release boundaries, and hygiene;
- root GitHub CI that runs the visible demo commands across all ten demos;
- an executable decoy fail-open proof that demonstrates the harness catches a known no-effect regression.

The v0.4.1 result is intentionally described as an internal adversarial harness pass, not an independent external red-team certification. The machine-readable result is recorded in:

```text
reports/adversarial_harness_report.json
reports/decoy_fail_open/summary.json
```

## v0.4.2 public links polish

This docs-only polish release adds Maxwell Evidence public links to the suite documentation and demo README files:

- Website: https://www.maxwellevidence.com/
- YouTube: https://www.youtube.com/@MaxwellEvidence

No runtime demo logic, policies, adversarial harness behavior, or effect-record behavior changed in v0.4.2.

## Core invariant

```text
any downstream effect artifact is emitted
  => policy permits effect
  AND evidence is complete
  AND authority is valid
  AND action is in scope
  AND required review/security/due-process conditions are satisfied
```

## Boundary

These are public-safe local demos. They are not production deployments, legal advice, certification claims, or a complete disclosure of private Maxwell internals.
