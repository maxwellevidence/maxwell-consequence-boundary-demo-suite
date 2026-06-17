# Claims and Limitations

## What this demo claims

This demo claims only that, in this deterministic local public preview:

- prompt-injected instructions are preserved as evidence, not accepted as authority;
- LLM-generated authority claims do not create trusted approval;
- out-of-bound tool requests do not create downstream effect records;
- clean requests with sufficient evidence and role scope can create a bounded effect record;
- generated artifacts can be verified against a manifest.

## What this demo does not claim

This demo is not:

- a production prompt-injection detector;
- a complete runtime security product;
- legal, compliance, or certification guidance;
- the full Maxwell Evidence architecture;
- a replacement for identity, access management, secure runtime controls, or human review;
- a claim that prompts cannot influence model output.

The demo focuses on the consequence boundary: model output alone cannot authorize downstream effect.


## v0.4.0 adversarial harness boundary

The adversarial harness is an internal public-preview exercise over synthetic local inputs. It is not an independent third-party red-team validation and is not a production-security certification.
