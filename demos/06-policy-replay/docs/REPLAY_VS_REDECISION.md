# Replay vs. Redecision

Policy replay asks:

```text
What would the same frozen evidence and authority context produce under a newer policy?
```

It does not ask:

```text
Should we rewrite the original action?
```

In this demo, replay reports are written to `artifacts/replay/`. The original
run folders under `artifacts/runs/` are not mutated by replay.

This distinction matters because enterprise records often need to preserve what
was known, what policy applied, and what authority existed at the time of action.
