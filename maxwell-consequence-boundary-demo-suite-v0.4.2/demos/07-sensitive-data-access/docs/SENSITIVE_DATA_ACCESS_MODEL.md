# Sensitive Data Access Model

This demo models a narrow public-safe version of a governed AI retrieval boundary.

The evaluated dimensions are:

```text
role
purpose
dataset scope
data classification
legal basis
data minimization
requested fields
downstream target system
prompt-injection boundary
```

The model intentionally does not return actual records. It creates an effect record only when the
synthetic policy says the access effect is permitted.

## Why this matters

Enterprise AI systems often treat retrieval as a model/tooling problem. This demo frames retrieval
as a consequence boundary: once an AI workflow can access or expose sensitive data, the
organization needs evidence, authority, policy, and reconstruction.

## Maxwell framing

```text
AI request -> evidence captured -> authority evaluated -> policy reason -> effect or no effect
```
