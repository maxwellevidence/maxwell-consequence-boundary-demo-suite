"""Public OIDC authority-context validator.

This is a real signed-token validation seam for reviewer testing. It validates
JWT signature, issuer, audience, expiration, scope, and role claims, then maps
successful claims into the public authority-context shape used by the gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

import jwt


@dataclass(frozen=True)
class OIDCValidationResult:
    valid: bool
    authority_context: dict[str, Any]
    reason_codes: list[str]


def validate_oidc_token_to_authority_context(
    token: str,
    public_key_pem: str | bytes,
    *,
    issuer: str,
    audience: str | Sequence[str],
    required_scope: str,
    required_roles: list[str] | tuple[str, ...],
    algorithms: list[str] | tuple[str, ...] = ("RS256",),
) -> OIDCValidationResult:
    """Validate a signed OIDC/OAuth token and map it into authority context.

    Invalid tokens fail closed by returning a non-authoritative context with
    ``oauth_status="invalid"``. The raw token is never written to artifacts.
    """

    try:
        claims = jwt.decode(
            token,
            public_key_pem,
            algorithms=list(algorithms),
            issuer=issuer,
            audience=audience,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except Exception as exc:  # public-safe: expose type, not raw token details
        return OIDCValidationResult(
            valid=False,
            authority_context=_invalid_authority_context(),
            reason_codes=["OIDC_TOKEN_VALIDATION_FAILED", exc.__class__.__name__],
        )

    scopes = _split_scopes(claims.get("scope") or claims.get("scp"))
    roles = _as_list(claims.get("roles") or claims.get("role"))

    if required_scope not in scopes:
        return OIDCValidationResult(
            valid=False,
            authority_context=_invalid_authority_context(subject=claims.get("sub")),
            reason_codes=["OIDC_REQUIRED_SCOPE_MISSING"],
        )

    if not set(roles).intersection(set(required_roles)):
        return OIDCValidationResult(
            valid=False,
            authority_context=_invalid_authority_context(subject=claims.get("sub")),
            reason_codes=["OIDC_REQUIRED_ROLE_MISSING"],
        )

    return OIDCValidationResult(
        valid=True,
        authority_context={
            "oauth_status": "complete",
            "subject": claims.get("sub"),
            "issuer": claims.get("iss"),
            "audience": claims.get("aud"),
            "expires_at": _exp_to_iso8601(claims.get("exp")),
            "scopes": scopes,
            "roles": roles,
            "token_claims_bound": True,
        },
        reason_codes=["OIDC_TOKEN_VALIDATED", "AUTHORITY_CONTEXT_MAPPED_FROM_SIGNED_TOKEN"],
    )


def _invalid_authority_context(subject: Any = "unverified") -> dict[str, Any]:
    return {
        "oauth_status": "invalid",
        "subject": str(subject or "unverified"),
        "issuer": "unverified",
        "audience": "unverified",
        "expires_at": "1970-01-01T00:00:00Z",
        "scopes": ["unverified"],
        "roles": ["unverified"],
        "token_claims_bound": False,
    }


def _split_scopes(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part for part in value.split() if part]
    return [str(item) for item in _as_list(value)]


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def _exp_to_iso8601(exp: Any) -> str:
    """Preserve the token's actual exp value as UTC ISO-8601."""

    if isinstance(exp, datetime):
        value = exp if exp.tzinfo else exp.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    if isinstance(exp, (int, float)):
        return (
            datetime.fromtimestamp(exp, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    return ""
