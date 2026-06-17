# Claims and Limitations — Public Preview v0.3.0

This package is **Demo 02** in the Maxwell Consequence Boundary Demo Suite.

## What this package demonstrates

- A public branching policy file reviewers can inspect and try to break.
- YAML-held issuer and audience trust roots.
- A fail-closed policy engine for malformed, stale, unauthorized, contradictory, incomplete, or out-of-scope inputs.
- Shape-named demo inputs whose filenames do not encode the expected outcome.
- A signed-token OIDC validation seam that maps verified claims into authority context.
- Good-token and multiple bad-token OIDC cases reachable from `make demo`.
- Bad-input matrix tests over action, evidence, and authority fields.
- Hypothesis property-based tests for fail-closed invariants.
- Replay/verification artifacts that make decision output inspectable after the fact.
- A repo-root RSA public key that verifies signatures over generated hash manifests.
- A public-safe MESI-style control pattern: evidence before effect.

## What changed in v0.3.0

- Added root `LICENSE` file for GitHub clarity.
- Added suite placement language so reviewers understand this as Demo 02.
- Added MESI / Effect Gate bridge language.
- Added package-check and clean-ZIP tooling.
- Moved reviewed sample outputs to `artifacts/sample_outputs/`.
- Updated fixture-key warnings so the committed private keys are unmistakably public demo material.

## What this package does not claim

- It is not a production deployment.
- It is not certified, audited, or NVIDIA-validated.
- It is not an official NVIDIA integration.
- It does not disclose Maxwell private authority logic, evaluator chains, thresholds, production trust roots, or production enforcement logic.
- It does not assert legal admissibility of records.
- It does not claim compliance by default with any statute, standard, procurement framework, or internal control regime.
- Its manifest signature is a repo-anchored demo mechanism, not an external timestamp, transparency log, third-party attestation, production signing root, or independent custody proof.
- The manifest signature detects modification of generated run artifacts only while the repo-root `MANIFEST_PUBLIC_KEY.pem` remains trusted; it is not a defense against an actor with write access to the repository root.
- The private keys under `fixtures/` are intentionally public demo material, not production secrets. Treat anything they sign as unauthenticated outside this proof.


## v0.4.0 adversarial harness boundary

The adversarial harness is an internal public-preview exercise over synthetic local inputs. It is not an independent third-party red-team validation and is not a production-security certification.
