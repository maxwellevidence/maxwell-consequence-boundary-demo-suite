# Demo Build Brief: Sensitive Data Access

## Suite position

Demo 07 of the Maxwell Consequence Boundary Demo Suite.

## Audience

Privacy teams, regulated-data owners, legal/compliance, healthcare, HR, financial-services
teams, enterprise AI builders, and technical reviewers.

## Primary invariant

```text
No valid role + purpose + data scope + evidence -> no data access effect record.
```

## Public hook

```text
AI retrieval is not automatically authorized access.
```

## Consequence boundary

A proposed AI retrieval/summarization/access action attempts to become a downstream access
effect. Maxwell creates the effect only when the demo policy is satisfied.

## Success criteria

- The valid case creates `data_access_effect_record.json`.
- Review cases create `review_ticket.json` and no effect record.
- Suppressed cases create `suppression_notice.json` and no effect record.
- `make verify` detects artifact tampering and effect/decision mismatches.
- No real sensitive data is included.
