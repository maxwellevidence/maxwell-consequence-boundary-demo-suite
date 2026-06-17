# OAuth/OIDC Authority Context — Public Preview v0.3.0

The public preview includes a signed-token validation seam in:

```text
src/maxwell_effect_gate/oidc_authority.py
```

The validator checks:

- JWT signature
- issuer
- audience
- expiration
- required scope
- required role

Successful validation maps token claims into the public `authority_context` consumed by the policy engine. Failed validation returns `oauth_status: invalid` and a non-authoritative context that fails closed.

## Demo visibility

`make demo` includes these OIDC cases:

```text
oidc_signed_token_run/
oidc_bad_token_wrong_audience_run/
oidc_bad_token_bad_signature_run/
oidc_bad_token_expired_run/
oidc_bad_token_missing_scope_run/
```

The demo signs tokens with:

```text
fixtures/oidc_demo_issuer_private_key.pem
```

The validator checks them against:

```text
fixtures/oidc_demo_issuer_public_key.pem
```

The expected issuer, expected audience list, required scope, and required roles are read from:

```text
policies/public_change_control_policy.yml
```

The raw token is not written to artifacts. Reviewers can inspect:

```text
artifacts/oidc_signed_token_run/oidc_validation_result.json
artifacts/oidc_bad_token_wrong_audience_run/oidc_validation_result.json
artifacts/oidc_bad_token_bad_signature_run/oidc_validation_result.json
artifacts/oidc_bad_token_expired_run/oidc_validation_result.json
artifacts/oidc_bad_token_missing_scope_run/oidc_validation_result.json
```

## Expiration handling

For valid tokens, the authority context preserves the token's real `exp` value as UTC ISO-8601. It does not replace the expiration with a placeholder.

## Public proof boundary

The included demo and tests use local fixture keys so reviewers can inspect behavior without requiring a live Auth0, Okta, Entra ID, Google, or Keycloak tenant.

The same validation seam can be wired to a live OIDC provider by supplying provider keys, issuer, audience, required scope, and required role.

This proves the authority-context validation path at public-preview scale. It does not claim production IAM integration, enterprise SSO certification, or third-party validation.
