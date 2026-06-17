# Policy Reason Codes

| Code | Meaning |
|---|---|
| `PROMPT_BOUNDARY_EFFECT_COMMITTED` | Evidence, authority, and tool boundary were sufficient. |
| `PROMPT_INJECTION_BOUNDARY_TRIGGERED` | Prompt-injected override language was detected and quarantined. |
| `UNTRUSTED_AUTHORITY_CLAIM` | Authority was claimed through model output, prompt text, chat text, or self-approval rather than a trusted source. |
| `TOOL_REQUEST_OUTSIDE_BOUNDARY` | The requested tool is prohibited or outside actor authority. |
| `MODEL_RISK_DOWNGRADE_REQUIRES_SECURITY_REVIEW` | The model attempted to relabel a higher-risk action as lower risk. |
| `MISSING_EVIDENCE_REQUIRES_REVIEW` | Required evidence was missing, so no effect was created. |
| `HIGH_RISK_REQUIRES_REVIEW` | The action exceeds the actor's no-review risk threshold. |
| `MISSING_ACTOR_AUTHORITY` | The actor does not have recognized authority. |
| `SCOPE_OR_TARGET_OUTSIDE_AUTHORITY` | The action scope, effect type, or target system is outside role authority. |
