# Policy Reason Codes

| Reason code | Meaning |
|---|---|
| `EFFECT_COMMITTED` | Initial evidence and proposer authority were sufficient. |
| `REVIEW_APPROVED_EFFECT_COMMITTED` | Controlled review supplied sufficient evidence and reviewer authority. |
| `REVIEW_REQUIRED_MISSING_EVIDENCE` | The action is reviewable, but required evidence is missing. |
| `REVIEW_REQUIRED_HIGH_RISK` | The action is high risk and requires human review. |
| `REVIEW_FAILED_MISSING_EVIDENCE` | Review was submitted but required evidence remains missing. |
| `REVIEWER_LACKS_AUTHORITY` | The reviewer lacks sufficient authority for the action. |
| `REVIEW_FAILED_REJECTED` | The reviewer did not approve the action. |
| `NON_REVIEWABLE_SCOPE_VIOLATION` | The original proposal is outside approved scope. |
| `PROMPT_INJECTION_NOT_AUTHORITY` | Prompt-injected override language is preserved but not treated as authority. |
| `REVIEW_SCOPE_EXPANSION_BLOCKED` | Review attempted to change the original scope, effect type, or target system. |
| `MISSING_AUTHORITY_CONTEXT` | The proposer lacks authority to propose the action. |
