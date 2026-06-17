# Output Schema Overview

Each run directory contains public-safe JSON artifacts.

## `input_request.json`

The original synthetic payment proposal.

## `payment_evidence_bundle.json`

A normalized bundle of payment evidence references, vendor status, amount, invoice id, and payment risk signals.

## `authority_context.json`

A normalized view of claimed payment authority, payment scope, approval limit, requester, approver, and dual-control context.

## `decision_receipt.json`

The policy-derived decision record. It includes:

- lifecycle state,
- payment reason code,
- review route when applicable,
- authority basis,
- payment amount,
- target system,
- and whether payment effect is permitted.

## `payment_effect_record.json`

Created only when payment effect is permitted. It is synthetic and does not initiate a real payment.

## `review_ticket.json`

Created for review-routed cases.

## `suppression_notice.json`

Created for suppressed cases.

## `NO_PAYMENT_EFFECT_CREATED.txt`

Created whenever payment effect is not permitted.

## `manifest.json`

A manifest of generated run files and their hashes.

## `verification_report.json`

Created by `make verify` after checking artifact consistency.
