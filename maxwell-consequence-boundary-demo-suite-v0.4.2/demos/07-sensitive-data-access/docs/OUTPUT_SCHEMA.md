# Output Schema Overview

Each run directory contains JSON artifacts with stable public-preview shapes.

## `data_evidence_bundle.json`

Records evidence references, purpose, legal basis, data minimization, prompt-injection detection,
and missing evidence.

## `authority_context.json`

Records actor role, dataset scope, data class clearance, requested fields, purpose scope, target
system scope, and whether access authority is present.

## `decision_receipt.json`

Records the policy-derived outcome and hashes of the evaluated evidence and authority context.

## `data_access_effect_record.json`

Created only when `decision_receipt.effect_permitted` is true. It does not contain sensitive data.

## `review_ticket.json`

Created when the request is routed to review.

## `suppression_notice.json`

Created when the request is suppressed.

## `manifest.json` and `verification_report.json`

Used by `make verify` to check artifact integrity and effect/decision consistency.
