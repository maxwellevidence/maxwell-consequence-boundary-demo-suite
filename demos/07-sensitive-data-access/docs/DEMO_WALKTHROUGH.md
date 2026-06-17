# Demo Walkthrough

Run:

```bash
make demo
make verify
```

Then inspect:

```text
artifacts/runs/01_valid_role_and_purpose/
```

You should see `data_access_effect_record.json`. That file records a permitted downstream data
access effect. It does not contain the underlying sensitive data.

Next inspect:

```text
artifacts/runs/05_prompt_injection_restricted_data/
```

You should see `suppression_notice.json` and `NO_DATA_ACCESS_EFFECT_CREATED.txt`, but no
`data_access_effect_record.json`. The malicious instruction is captured as part of the proposed
request, but it is not treated as authority.

## Lifecycle statuses

```text
access_effect_committed  -> downstream data-access effect record was created
review_routed            -> human/privacy review route was created; no effect record
access_suppressed        -> requested access was suppressed; no effect record
```

## Key inspection file

The most important file in each run is:

```text
decision_receipt.json
```

It records:

- lifecycle status,
- effect permission,
- reason code,
- policy hash,
- evidence hash,
- authority-context hash.
