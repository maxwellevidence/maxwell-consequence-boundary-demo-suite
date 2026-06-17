# Policy Replay Model

This demo separates three things:

```text
1. The original action record.
2. The policy used at the time.
3. The replay result under a later policy.
```

Policy replay is not reauthorization of the original action. It is a structured
comparison between the policy-at-the-time and a newer policy.

## Replay lifecycle

```text
ORIGINAL_RECORD_LOADED
ORIGINAL_INTEGRITY_VERIFIED
TARGET_POLICY_LOADED
FROZEN_EVIDENCE_REEVALUATED
DRIFT_CLASSIFIED
NO_RETROACTIVE_EFFECT_MUTATION
REPLAY_REPORT_WRITTEN
```

## Drift classes

```text
NO_OUTCOME_CHANGE
PREVIOUSLY_ALLOWED_NOW_REVIEW
PREVIOUSLY_ALLOWED_NOW_BLOCK
PREVIOUSLY_SUPPRESSED_NOW_ALLOWED
PREVIOUSLY_SUPPRESSED_STILL_SUPPRESSED
```
