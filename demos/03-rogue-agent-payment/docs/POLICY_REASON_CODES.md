# Payment Policy Reason Codes

| Reason code | Lifecycle state | Meaning |
|---|---|---|
| `PAYMENT_EFFECT_PERMITTED` | `PAYMENT_EFFECT_COMMITTED` | Evidence, vendor status, scope, amount, and authority are sufficient for this public demo policy. |
| `PAYMENT_REQUIRED_EVIDENCE_MISSING` | `PAYMENT_REVIEW_ROUTED` | Required payment evidence references are missing. |
| `PAYMENT_AUTHORITY_CONTEXT_MISSING` | `PAYMENT_REVIEW_ROUTED` | Claimed payment authority is missing or incomplete. |
| `PAYMENT_SCOPE_NOT_AUTHORIZED` | `PAYMENT_EFFECT_SUPPRESSED` | Claimed authority does not cover the payment target scope. |
| `PAYMENT_VENDOR_NOT_APPROVED` | `PAYMENT_EFFECT_SUPPRESSED` | Vendor status is not approved. |
| `PAYMENT_SELF_APPROVAL_SUPPRESSED` | `PAYMENT_EFFECT_SUPPRESSED` | Requester and approver are the same actor. |
| `PAYMENT_PROMPT_INJECTION_SUPPRESSED` | `PAYMENT_EFFECT_SUPPRESSED` | Instruction text attempts to bypass policy or manufacture authority. |
| `PAYMENT_DUAL_CONTROL_REQUIRED` | `PAYMENT_REVIEW_ROUTED` | Payment amount crosses the dual-control threshold and lacks second approval. |
| `PAYMENT_VENDOR_BANK_CHANGE_REVIEW` | `PAYMENT_REVIEW_ROUTED` | Vendor bank-account change requires controlled review. |
| `PAYMENT_AMOUNT_EXCEEDS_AUTHORITY_LIMIT` | `PAYMENT_REVIEW_ROUTED` | Claimed approver authority is insufficient for the payment amount. |
| `PAYMENT_REVIEW_REQUIRED_RISK` | `PAYMENT_REVIEW_ROUTED` | Risk level requires controlled review before payment effect. |
| `PAYMENT_MALFORMED_INPUT` | `PAYMENT_EFFECT_SUPPRESSED` | Required input fields are missing or malformed. |
