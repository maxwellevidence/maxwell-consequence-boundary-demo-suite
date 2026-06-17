# Output Schema

## Original run artifacts

Each case creates:

```text
input_request.json
original_evidence_bundle.json
original_authority_context.json
original_policy_snapshot.json
decision_receipt.json
effect_record.json or NO_EFFECT_CREATED.txt
manifest.json
verification_report.json
```

## Replay artifacts

Each replay creates:

```text
policy_replay_report.json
```

The replay report contains:

```text
original_decision
replay_decision
outcome_changed
drift_class
effect_record_existed_before_replay
effect_record_exists_after_replay
effect_record_mutated
```
