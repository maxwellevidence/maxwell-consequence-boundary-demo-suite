# Adversarial Review Guide

Try changing a non-permitted input so that the LLM recommendation says "approved." Then rerun the demo. The model statement should still not create authority unless the request also satisfies policy, evidence, role scope, and tool boundary.

Try editing a generated artifact under `artifacts/runs/` and run:

```bash
make verify
```

The verification report should detect the manifest mismatch.

Useful files to inspect:

```text
policies/prompt_injection_boundary_policy.yml
src/maxwell_prompt_injection_boundary/engine.py
examples/demo_inputs/
```
