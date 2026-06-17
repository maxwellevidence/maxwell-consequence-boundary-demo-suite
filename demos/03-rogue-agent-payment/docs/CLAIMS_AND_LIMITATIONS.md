# Claims and Limitations

## What this demo claims

This demo claims that, inside this local public-preview proof surface:

- A synthetic AI payment recommendation is not treated as financial authority.
- Payment evidence is captured before downstream effect is considered.
- Claimed approval authority is normalized into a reviewable authority context.
- Policy reason codes explain why payment effect is committed, routed, or suppressed.
- A synthetic payment effect record is created only when policy permits effect.
- Non-permitted cases do not create `payment_effect_record.json`.
- Generated artifacts can be verified later against manifest-bound hashes.

## What this demo does not claim

This demo does not claim to be:

- production Maxwell Evidence software,
- a payment processor,
- an accounts-payable integration,
- a fraud-detection product,
- a legal or compliance determination,
- an audit certification,
- an internal-control certification,
- a complete security product,
- or a disclosure of private Maxwell Evidence implementation details.

## Public-safe boundary

All data is synthetic. No real downstream payment system is contacted.


## v0.4.0 adversarial harness boundary

The adversarial harness is an internal public-preview exercise over synthetic local inputs. It is not an independent third-party red-team validation and is not a production-security certification.
