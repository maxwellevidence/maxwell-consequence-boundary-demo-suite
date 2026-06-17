# Public Sector Determination Model

This demo models a simplified public-sector consequence boundary:

```text
AI recommendation
  -> proposed determination
  -> evidence bundle
  -> actor authority context
  -> due-process context
  -> review authority context when needed
  -> decision receipt
  -> determination effect record or no-effect artifact
```

## Key concept

A public-sector determination is more than a prediction or recommendation. In this demo, a proposed determination becomes downstream effect only when the record supports it.

## Reviewable artifacts

Each run emits:

```text
input_request.json
policy_snapshot.json
determination_evidence_bundle.json
authority_context.json
review_authority_context.json
due_process_analysis.json
decision_receipt.json
determination_effect_record.json or NO_DETERMINATION_EFFECT_CREATED.txt
manifest.json
verification_report.json
```

## Effect boundary

The demo creates `determination_effect_record.json` only for permitted cases. Non-permitted cases create review or suppression artifacts instead.
