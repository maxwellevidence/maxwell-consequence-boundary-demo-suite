# Adversarial Review Notes — Demo 02

This v0.3.3 starter layer adds hostile inputs and tests for the public fail-closed invariant.

## Property under test

```text
No sufficient evidence + authority + scope + required review/security context -> no downstream effect artifact.
```

## Current starter corpus

See:

```text
examples/adversarial_inputs/
tests/adversarial/test_adversarial_corpus.py
```

## Expected behavior

Adversarial cases should not create `effect_record.json`. They should route to review, quarantine, suppression, pause, or block depending on the demo.

## Not yet claimed

This starter corpus is not a full independent red-team report and is not exhaustive. The next credibility layer is mutation testing and expanded property-based fuzzing.

## v0.3.4 mutation and fuzzing starter

Additional reviewer checks are now available:

```bash
make fuzz-quick
make mutation-smoke
```

`make fuzz-quick` runs dependency-light fail-closed input-space tests. `make mutation-smoke` plants four known fail-open mutants in a temporary package copy and requires the test suite to kill them. See `docs/MUTATION_AND_FUZZING.md` for scope and limitations.
