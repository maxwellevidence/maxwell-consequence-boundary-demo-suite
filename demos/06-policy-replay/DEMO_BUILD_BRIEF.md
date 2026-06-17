# Demo Build Brief

## Demo

Maxwell Policy Replay Demo v0.1.0

## Suite position

Demo 06 of the Maxwell Consequence Boundary Demo Suite.

## Attention hook

Same evidence. New policy. No retroactive effect mutation.

## Primary invariant

```text
Policy replay may change the replay result, but it must not rewrite the original effect record.
```

## Secondary invariant

```text
The original decision remains tied to the policy version used at the time.
```

## Demo audiences

- AI governance reviewers
- Enterprise risk teams
- Compliance and audit reviewers
- Technical diligence reviewers
- Builders of agentic AI workflows

## Public-safe boundaries

This demo uses synthetic policies, synthetic actors, synthetic evidence, and
synthetic downstream effects. It does not include private Maxwell internals.
