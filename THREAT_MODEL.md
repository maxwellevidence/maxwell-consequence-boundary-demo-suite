# Threat Model — Maxwell Consequence Boundary Demo Suite v0.4.0

## Public fail-closed invariant

For every public-demo input `i`:

```text
any downstream effect artifact is emitted
  => policy(i) permits effect
  AND evidence_complete(i)
  AND authority_valid(i)
  AND action_in_scope(i)
  AND any required review, security, or due-process condition is satisfied.
```

A break is any input that creates a downstream effect artifact without satisfying the public policy, evidence, authority, scope, and review conditions for that demo.

## Win conditions for an adversarial reviewer

An adversarial reviewer wins if they can:

```text
1. obtain an effect artifact without legitimate allow/permitted effect status;
2. cause a committed effect to become non-reconstructable while verification still passes;
3. forge or mutate a manifest or decision receipt in a way that the verifier accepts;
4. widen authority, scope, role, or delegation by encoding hostile claims in free text, metadata, or model output.
```

## Attack classes in scope for this public suite

The v0.4.0 starter corpus covers these public-safe attack families:

```text
Authority bypass
Policy bypass
Scope widening
Prompt injection carried in otherwise valid-looking evidence
Type coercion and malformed input
Fake approver / fake review claims
Manifest or artifact tampering
Evidence deletion or evidence-packet loss
Unsafe public-sector determination attempts
```

The flagship technical review demo also includes signed-token and manifest-verification attack tests.

## Out-of-scope boundaries

These demos are local deterministic public proofs. They do not claim production deployment, legal advice, certification, full security coverage, real downstream execution, or disclosure of non-public Maxwell implementation internals.

The public verifier and artifact model are designed for transparent review of this demo suite. They are not a production signing service, external timestamping system, transparency log, or third-party attestation system.

## Reviewer procedure

For each demo:

```bash
make demo
make verify
make test
make package-check
```

The adversarial corpus is located at:

```text
examples/adversarial_inputs/
tests/adversarial/
```

Every adversarial input is expected to route to review, quarantine, suppression, or block. No adversarial input should create a downstream effect artifact.
