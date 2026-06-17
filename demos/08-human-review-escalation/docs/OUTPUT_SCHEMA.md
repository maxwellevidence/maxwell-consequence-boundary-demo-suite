# Output Schema

Each case produces a directory under `artifacts/runs/<case_id>/`.

Common files:

- `input_request.json`
- `policy_snapshot.json`
- `initial_evidence_bundle.json`
- `initial_authority_context.json`
- `initial_decision_receipt.json`
- `decision_receipt.json`
- `manifest.json`
- `verification_report.json`

Review files:

- `review_event.json`
- `review_authority_context.json`
- `review_ticket.json`
- `review_rejection_notice.json`

Effect files:

- `authorized_effect_record.json` when final effect is permitted.
- `NO_AUTHORIZED_EFFECT_CREATED.txt` when final effect is not permitted.
- `suppression_notice.json` when effect is suppressed outside a pending review path.
