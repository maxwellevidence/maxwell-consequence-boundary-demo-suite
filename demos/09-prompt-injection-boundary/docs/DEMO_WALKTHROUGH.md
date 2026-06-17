# Demo Walkthrough

Run:

```bash
make demo
make verify
```

## Clean path

`01_normal_instruction_valid` creates `bounded_effect_record.json` because the request is within role scope, evidence is complete, and the tool is permitted.

## Prompt-injection path

`02_ignore_policy_instruction` and `03_urgent_override_attempt` create `quarantine_ticket.json` and `NO_BOUNDARY_EFFECT_CREATED.txt`. The suspicious instruction is preserved in `input_request.json` and analyzed in `prompt_boundary_analysis.json`.

## Fake authority path

`04_fake_manager_approval` suppresses effect because an LLM-generated manager-approval claim is not trusted authority.

## Tool-boundary path

`05_malicious_tool_request` suppresses effect because the requested tool is prohibited and outside the actor's permitted boundary.

## Review path

`06_model_relabels_high_risk_low` routes to security review because the model relabeled a higher-risk action as low risk. No effect is created.
