# Policy Reason Codes

| Reason code | Meaning | Lifecycle |
|---|---|---|
| `DELEGATED_EFFECT_PERMITTED` | Delegation, scope, target system, and evidence continuity are sufficient. | `DELEGATED_EFFECT_COMMITTED` |
| `DELEGATION_SCOPE_MISSING_REVIEW` | Delegation exists but does not include the requested downstream scope. | `DELEGATION_REVIEW_ROUTED` |
| `AGENT_SCOPE_EXPANSION_SUPPRESSED` | Executing agent expanded the action beyond delegated task scope. | `DELEGATED_EFFECT_SUPPRESSED` |
| `DELEGATION_WRONG_SYSTEM_SUPPRESSED` | Delegated authority was reused for a different target system. | `DELEGATED_EFFECT_SUPPRESSED` |
| `DELEGATION_EVIDENCE_PACKET_MISSING` | Evidence packet was missing or no longer bound to the handoff. | `DELEGATION_REVIEW_ROUTED` |
| `DELEGATION_PROMPT_INJECTION_SUPPRESSED` | Instruction text attempted to bypass or manufacture authority. | `DELEGATED_EFFECT_SUPPRESSED` |
| `DELEGATION_CHAIN_MISMATCH_SUPPRESSED` | Delegator/delegatee identities do not match the handoff. | `DELEGATED_EFFECT_SUPPRESSED` |
| `DELEGATION_EXPIRED_SUPPRESSED` | Claimed delegation is expired. | `DELEGATED_EFFECT_SUPPRESSED` |
| `DELEGATION_EXECUTION_NOT_GRANTED_REVIEW` | Delegation does not permit downstream execution. | `DELEGATION_REVIEW_ROUTED` |
| `MULTI_AGENT_MALFORMED_INPUT` | Required input fields are missing. | `DELEGATED_EFFECT_SUPPRESSED` |
