# Policy Reason Codes

The synthetic policies use these reason codes:

| Reason code | Meaning |
|---|---|
| `PR_POLICY_ALLOW` | Evidence, authority, scope, and risk requirements passed. |
| `PR_REVIEW_REQUIRED_EVIDENCE_MISSING` | Required evidence is missing under the evaluated policy. |
| `PR_BLOCK_MISSING_AUTHORITY` | No valid authority context supports downstream effect. |
| `PR_BLOCK_SCOPE_VIOLATION` | The target system is outside the approver's scope. |
| `PR_BLOCK_EFFECT_NOT_IN_ROLE_SCOPE` | The role is not permitted to commit the requested effect type. |
| `PR_REVIEW_ROLE_INSUFFICIENT` | The role does not meet the minimum role for the effect. |
| `PR_REVIEW_APPROVER_ROLE_REQUIRED` | A policy-specific approver role is required. |
| `PR_REVIEW_DUAL_CONTROL_REQUIRED` | Dual control is required under the evaluated policy. |
| `PR_REVIEW_ROLE_RISK_LIMIT` | The requested risk exceeds the role profile. |
| `PR_REVIEW_RISK_THRESHOLD` | The request meets the policy review threshold. |
| `PR_BLOCK_FORBIDDEN_EFFECT` | The requested effect type is not allowed by policy. |

Reason codes are synthetic and intentionally simplified.
