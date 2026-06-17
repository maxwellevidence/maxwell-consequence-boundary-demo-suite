# Policy Reason Codes — Public Preview v0.3.0

Reason codes are public-safe labels emitted in `decision_receipt.json`. They identify the policy branch or fail-closed condition without disclosing Maxwell private authority logic.

## Allow-path codes

| Code | Meaning |
|---|---|
| `AUTHORITY_CONTEXT_SUFFICIENT` | The supplied authority context satisfied the public allow branch. |
| `EVIDENCE_BUNDLE_PRESENT` | Required evidence fields were present. |
| `POLICY_BRANCH_ALLOW_STAGING_BOUNDED_CHANGE` | The bounded staging allow branch matched. |

## Pause-path codes

| Code | Meaning |
|---|---|
| `HUMAN_APPROVAL_REQUIRED` | The request is bounded but missing required dual-control authority. |
| `HOLD_EFFECT_PENDING_ADDITIONAL_AUTHORITY` | Downstream effect is held at the consequence boundary. |

## Block-path codes

| Code | Meaning |
|---|---|
| `MALFORMED_PUBLIC_INPUT` | Required action, evidence, or authority fields are missing or empty. |
| `NO_EFFECT_INVALID_SHAPE` | The public input shape is not sufficient for effect. |
| `UNKNOWN_ACTION_TYPE` | The requested action type is outside the policy's allowed values. |
| `NO_EFFECT_OUT_OF_SCOPE_ACTION` | The action is outside the public effect boundary. |
| `INVALID_OR_ABSENT_OAUTH_CONTEXT` | OAuth/OIDC authority is not complete. |
| `NO_EFFECT_INVALID_AUTHORITY` | Authority is invalid or absent. |
| `INVALID_ISSUER_OR_AUDIENCE` | Issuer or audience does not match YAML trust roots. |
| `AUTHORITY_CONTEXT_EXPIRED` | Authority context is stale. |
| `NO_EFFECT_STALE_AUTHORITY` | Stale authority cannot create downstream effect. |
| `SELF_APPROVAL_NOT_PERMITTED` | Requester and approver are the same actor. |
| `NO_EFFECT_DUAL_CONTROL_FAILURE` | Dual-control requirements failed. |
| `PRODUCTION_HIGH_RISK_REQUIRES_DUAL_CONTROL` | Production high/critical request lacks dual control. |
| `NO_MATCHING_POLICY_BRANCH` | No explicit allow or pause branch matched. |
| `NO_EFFECT_DEFAULT_BLOCK` | Default-block fallback prevented downstream effect. |

## OIDC validation result codes

These appear in `oidc_validation_result.json`, not necessarily in the decision receipt.

| Code | Meaning |
|---|---|
| `OIDC_TOKEN_VALIDATED` | Signature, issuer, audience, expiration, scope, and role checks passed. |
| `AUTHORITY_CONTEXT_MAPPED_FROM_SIGNED_TOKEN` | Valid token claims were mapped into authority context. |
| `OIDC_TOKEN_VALIDATION_FAILED` | The token failed validation, such as wrong audience, bad signature, expired token, or bad issuer. |
| `OIDC_REQUIRED_SCOPE_MISSING` | The token validated structurally but lacked the required scope. |
| `OIDC_REQUIRED_ROLE_MISSING` | The token validated structurally but lacked the required role. |

## Authoring behavior

Unknown policy predicates and operators warn and fail closed. They do not create an allow branch.
