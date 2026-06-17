# Claims and Limitations

## What this demo claims

This public preview demonstrates a local policy-replay control pattern:

```text
A prior AI-assisted action can be replayed under a newer policy without rewriting the original record.
```

It also shows that replay can identify outcome drift:

```text
allow -> review
allow -> block
block -> allow
no change
```

## What this demo does not claim

This demo is not:

- production governance software,
- a legal or compliance opinion,
- a certification claim,
- a full Maxwell architecture disclosure,
- a security boundary for real systems,
- a replacement for legal, audit, privacy, or risk review.

All examples are synthetic.


## v0.4.0 adversarial harness boundary

The adversarial harness is an internal public-preview exercise over synthetic local inputs. It is not an independent third-party red-team validation and is not a production-security certification.
