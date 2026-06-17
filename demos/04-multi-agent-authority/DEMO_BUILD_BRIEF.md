# Demo Build Brief

## Demo name

Maxwell Multi-Agent Authority Demo

## Suite position

Demo 04 in the Maxwell Consequence Boundary Demo Suite.

## Attention hook

Task handoff is not authority handoff.

## Public-safe proof

The demo shows that an executing agent can receive a task from another agent but
still fail to create a downstream effect unless the evidence packet, delegation
chain, target scope, and target system are valid.

## Invariant

```text
No valid delegated authority + evidence continuity -> no delegated downstream effect record.
```

## Intended audience

- AI agent builders
- Enterprise AI governance teams
- Security and platform reviewers
- Technical investors or diligence reviewers

## Deliberate boundaries

- Synthetic examples only
- No production identity system
- No private Maxwell architecture disclosure
- No real agent orchestration framework dependency
