# Human Review Escalation Model

This public-preview model treats review as a controlled transition, not an override.

A proposed action can move through these lifecycle states:

```text
PROPOSED
EVIDENCE_CAPTURED
INITIAL_AUTHORITY_EVALUATED
REVIEW_ROUTED
REVIEW_AUTHORITY_EVALUATED
REVIEW_APPROVED_EFFECT_COMMITTED
REVIEW_REJECTED_EFFECT_SUPPRESSED
EFFECT_SUPPRESSED
VERIFIED
```

The key control is that a reviewer cannot create effect simply by saying yes. Maxwell evaluates:

- whether the original proposal was reviewable,
- whether the reviewer has authority,
- whether the reviewer is independent from the proposer,
- whether evidence is complete after review,
- whether review stays within the original scope,
- whether the final effect is reconstructable.
