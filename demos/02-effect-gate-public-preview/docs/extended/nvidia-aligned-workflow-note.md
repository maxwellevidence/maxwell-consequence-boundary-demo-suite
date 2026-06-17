# Future Integration Note — NVIDIA Ecosystem

This optional note is not part of the core public proof.

The v0.3.0 public-preview package does **not** include an NVIDIA integration. It does not claim NVIDIA validation, approval, certification, endorsement, partnership, official integration, or production readiness.

A future integration could place the Maxwell Effect Gate after an agent workflow produces an action proposal and before that proposal creates a downstream enterprise record. In this public package, the runnable proof is framework-neutral:

```text
agent/workflow proposal
→ evidence bundle
→ authority context
→ policy_engine.evaluate_policy(...)
→ effect record only when policy returns allow
```

Reviewers should evaluate the current package by running:

```bash
make demo
make verify
make test
```

The core proof does not depend on NVIDIA tooling.
