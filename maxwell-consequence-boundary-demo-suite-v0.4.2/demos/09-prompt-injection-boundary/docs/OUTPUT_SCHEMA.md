# Output Schema

Each run directory may contain:

```text
input_request.json
policy_snapshot.json
instruction_evidence_bundle.json
authority_context.json
prompt_boundary_analysis.json
decision_receipt.json
bounded_effect_record.json
NO_BOUNDARY_EFFECT_CREATED.txt
security_review_ticket.json
quarantine_ticket.json
suppression_notice.json
manifest.json
verification_report.json
```

The core rule is simple:

```text
If decision_receipt.effect_permitted is false, bounded_effect_record.json must not exist.
```
