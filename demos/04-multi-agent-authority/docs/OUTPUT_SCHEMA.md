# Output Schema Overview

Each run creates a small set of JSON artifacts.

## `handoff_evidence_bundle.json`

Summarizes the synthetic evidence packet and evidence-continuity status.

## `authority_context.json`

Summarizes the claimed delegated authority available to the executing agent.

## `delegation_chain.json`

Shows the public-safe handoff chain from initiating agent to executing agent.

## `decision_receipt.json`

The policy-derived decision. This is the center of the run.

## `delegated_effect_record.json`

Created only when `decision_receipt.effect_permitted` is true.

## `review_ticket.json`

Created when the decision is routed to review.

## `suppression_notice.json`

Created when the decision is suppressed.

## `manifest.json`

Hashes the run artifacts so later verification can detect tampering.
