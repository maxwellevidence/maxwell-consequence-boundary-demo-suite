# Output Schema

This demo emits simple JSON records. The fields are intentionally explicit so reviewers can inspect the consequence boundary.

## Main output types

```text
determination_evidence_bundle.json
authority_context.json
review_authority_context.json
due_process_analysis.json
decision_receipt.json
determination_effect_record.json
case_review_ticket.json
due_process_review_ticket.json
suppression_notice.json
manifest.json
verification_report.json
```

## Decision receipt

The decision receipt includes:

```text
policy_id
policy_version
policy_hash
determination_evidence_bundle_hash
authority_context_hash
review_authority_context_hash
due_process_analysis_hash
decision
lifecycle_status
effect_permitted
reason_code
```

## Effect record

The effect record is intentionally synthetic. It records what would have been permitted; it does not call any public-sector system.
