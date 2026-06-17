# Maxwell Consequence Boundary Demo Suite

## Maxwell Evidence

Maxwell Evidence builds infrastructure for governed enterprise AI at the boundary where AI output becomes downstream consequence.

Website: https://www.maxwellevidence.com/
YouTube: https://www.youtube.com/@MaxwellEvidence


## Uniform spine, variable head

Every demo in this suite proves the same fail-closed property under a different consequence boundary:

```text
For every input i, a downstream effect artifact is emitted only if policy, evidence, authority, scope, and required review conditions are satisfied for i.
```

The shared mechanism is deliberate. It lets reviewers compare ten different threat stories against the same public control pattern.

## Demo sequence

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

## Three-phase release frame

1. **Attention:** Demos 01-05 establish the basic gate, the flagship technical review, payment authority, multi-agent authority, and reconstruction.
2. **Enterprise depth:** Demos 06-08 add policy replay, sensitive-data access, and human review.
3. **Expansion:** Demos 09-10 cover prompt-injection boundary control and public-sector due-process determinations.


## v0.4.0 adversarial starter

Each demo now includes `THREAT_MODEL.md`, `examples/adversarial_inputs/`, `tests/adversarial/`, and `docs/ADVERSARIAL_REVIEW_NOTES.md`. The starter corpus is designed to test fail-closed behavior under hostile but public-safe inputs.

## v0.4.0 release-candidate adversarial pass

The suite now includes a reproducible internal adversarial harness, rules of engagement, and a launch-candidate checklist. The harness runs the adversarial corpus for all ten demos through a common suite command:

```bash
make adversarial-harness
```

The pass is intentionally bounded: it is public-preview adversarial testing, not an independent security certification.


## v0.4.1 GitHub CI and decoy-proof polish

The active root GitHub workflow now runs `make ci-full`, which exercises the public demo commands across the monorepo rather than only the suite launch-check layer. The suite also includes an executable decoy fail-open proof: `make decoy-proof` plants a known forbidden-effect bug in a temporary copy of Demo 02 and verifies that the tests catch it.


## v0.4.2 public links polish

This release adds the public Maxwell Evidence website and YouTube channel references to the root suite documentation and each demo README. The links are informational only; the demos remain local and deterministic.

- Website: https://www.maxwellevidence.com/
- YouTube: https://www.youtube.com/@MaxwellEvidence
