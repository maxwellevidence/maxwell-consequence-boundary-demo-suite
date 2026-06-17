# Policy Reason Codes

| Code | Meaning |
|---|---|
| `DATA_ACCESS_EFFECT_COMMITTED` | Evidence, authority, purpose, scope, class, and minimization requirements are satisfied. |
| `DATA_PURPOSE_MISSING` | The request does not state a business purpose. |
| `DATA_EVIDENCE_INCOMPLETE` | Required evidence references are missing. |
| `DATA_AUTHORITY_MISSING` | The actor role is missing, unknown, or lacks data-access authority. |
| `DATASET_SCOPE_VIOLATION` | The requested dataset is outside the actor role's authorized scope. |
| `DATA_ROLE_NOT_AUTHORIZED` | The actor role is not authorized for the dataset under policy. |
| `DATA_CLASSIFICATION_EXCEEDS_CLEARANCE` | The data class exceeds the role's policy clearance. |
| `DATA_PURPOSE_OUTSIDE_SCOPE` | The stated purpose is not approved for the role or dataset. |
| `DATA_LEGAL_BASIS_MISSING` | Legal basis is required for the dataset/class but is not present. |
| `DATA_RESTRICTED_FIELD_REQUESTED` | The request includes restricted fields without sufficient approval. |
| `DATA_MINIMIZATION_REVIEW_REQUIRED` | The request is too broad or lacks data-minimization evidence. |
| `PROMPT_INJECTION_NOT_AUTHORITY` | A prompt-injected instruction was detected; output is not authority. |
| `DATA_TARGET_SYSTEM_SCOPE_VIOLATION` | The downstream target system is not authorized for this role. |
| `DATA_EFFECT_FORBIDDEN` | The requested data effect type is not allowed by the policy. |
