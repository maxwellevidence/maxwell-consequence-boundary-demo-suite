# Optional Execution-Surface Mapping

This optional note is future-integration framing only. The current v0.3.0 public-preview package is framework-neutral and does not include NVIDIA code, NVIDIA infrastructure, or NVIDIA validation.

The reusable boundary is:

```text
workflow output/action proposal
→ public evidence bundle
→ authority context, including OIDC-derived authority where applicable
→ public policy evaluation
→ downstream effect only on allow
```

A future agent-runtime wrapper could generate `action_proposal.json` and `evidence_bundle.json`, then call:

```python
evaluate_policy(action_proposal, evidence_bundle, authority_context)
```

That future wrapper would be integration work. It is not claimed by this repository.
