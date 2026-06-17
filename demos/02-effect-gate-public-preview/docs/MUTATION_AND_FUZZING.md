# Mutation and Fuzzing Notes

This public preview now includes a bounded credibility harness for the gate-critical path.

## What this adds

The normal test suite proves expected behavior on curated cases. The v0.3.4 credibility pass adds two additional layers:

1. **Expanded fail-closed input-space fuzzing** under `tests/fuzz/`.
2. **A bounded mutation-smoke harness** under `tools/gate_mutation_smoke.py`.

These are not production certification claims and they are not a full external red-team result. They are public, reproducible checks that make the flagship harder to accidentally regress into a fail-open state.

## Commands

Run the dependency-light input-space fuzz set:

```bash
make fuzz-quick
```

Run the fail-open sentinel smoke harness:

```bash
make mutation-smoke
```

Run the full reviewer path:

```bash
pip install -e ".[dev]"
make lint
make demo
make verify
make samples
make test
make fuzz-quick
make mutation-smoke
make package-check
```

## Mutation-smoke scope

The bounded harness runs bounded fail-open sentinel probes against gate-critical behavior. Current fail-open sentinel classes target:

| Mutant | Critical property stressed |
|---|---|
| Missing public inputs no longer detected | Missing evidence/authority/action fields must remain fail-closed. |
| Pause and block create effect records | Only policy-derived allow may produce `effect_record.json`. |
| Manifest signature always verifies | Manifest tampering and wrong-key signatures must be rejected. |
| Scope substring confusion accepted | Required scopes must match exactly, not by substring. |

A pass means the selected fail-closed probes killed all bounded fail-open sentinel classes. It does **not** mean every possible source-level mutant has been generated or triaged.

## Expanded fail-closed fuzzing scope

`tests/fuzz/test_fail_closed_input_space.py` generates deterministic hostile public-input shapes across:

- action proposal fields,
- evidence bundle fields,
- authority context fields,
- type confusion,
- nested objects,
- unicode edge cases,
- numeric edge cases,
- stale authority contexts,
- scope/role/audience confusion.

The key assertion is:

```text
If the gate emits downstream effect, then the action is in scope, the evidence is complete, and the authority context is valid.
```

## Hypothesis property tests

The flagship also includes Hypothesis-based tests. They run when the dev dependency set is installed with:

```bash
pip install -e ".[dev]"
```

If a reviewer runs without dev dependencies, the Hypothesis module reports as skipped rather than failing at import time.

## Bounded claim

This credibility layer is a public-preview safety net. It does not claim:

- complete production security coverage,
- external certification,
- independent red-team completion,
- full Maxwell private architecture disclosure,
- real downstream execution safety.

It does support the public preview's falsifiable claim:

```text
No policy-derived allow -> no downstream effect record.
```


## v0.4.0 update

The `mutation-smoke` target is now a fast fail-open sentinel-probe harness suitable for public-preview CI. It remains a bounded credibility layer, not a full mutation-testing score.
