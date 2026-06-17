# Output Schema

Each run directory contains a small set of inspectable artifacts.

```text
artifacts/runs/<case>/
  input_request.json
  evidence_bundle.json
  authority_context.json
  decision_receipt.json
  effect_record.json       # only if effect_permitted=true
  NO_EFFECT_CREATED.txt    # only if effect_permitted=false
  manifest.json
  verification_report.json # created by make verify
```

## `decision_receipt.json`

Key fields:

- `case_id`
- `outcome`
- `lifecycle_state`
- `reason_code`
- `effect_permitted`
- `review_route`
- `policy_id`
- `policy_version`
- `evidence_bundle_id`
- `authority_actor_id`
- `decision_receipt_id`

## `effect_record.json`

Created only when `effect_permitted=true`. It is bound to the decision receipt by `decision_receipt_sha256`.

## `NO_EFFECT_CREATED.txt`

Created when `effect_permitted=false`. This makes absence explicit and reviewable.

## `manifest.json`

Binds generated files to hashes so tampering can be detected by `make verify`.
