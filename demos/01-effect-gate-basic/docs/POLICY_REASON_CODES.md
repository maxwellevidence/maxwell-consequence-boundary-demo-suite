# Policy Reason Codes

| Reason code | Lifecycle state | Meaning |
|---|---:|---|
| `EFFECT_GATE_EFFECT_PERMITTED` | `EFFECT_COMMITTED` | Evidence, authority, scope, and risk were sufficient under the demo policy. |
| `EFFECT_GATE_REQUIRED_EVIDENCE_MISSING` | `REVIEW_ROUTED` | Required evidence references were missing, so no downstream effect was created. |
| `EFFECT_GATE_AUTHORITY_CONTEXT_MISSING` | `REVIEW_ROUTED` | Claimed authority was absent or could not execute the requested effect. |
| `EFFECT_GATE_SCOPE_NOT_AUTHORIZED` | `EFFECT_SUPPRESSED` | The requested target scope was outside the actor's claimed authority. |
| `EFFECT_GATE_REVIEW_REQUIRED_HIGH_RISK` | `REVIEW_ROUTED` | The risk level requires review before effect can be committed. |
| `EFFECT_GATE_PROMPT_INJECTION_SUPPRESSED` | `EFFECT_SUPPRESSED` | Instruction text attempted to bypass authority or governance. |
| `EFFECT_GATE_MALFORMED_INPUT` | `EFFECT_SUPPRESSED` | Required input fields were missing. |

The important pattern is not the label. The important pattern is that non-permitted outcomes do not create `effect_record.json`.
