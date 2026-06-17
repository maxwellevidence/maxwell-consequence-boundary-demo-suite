"""Public policy engine for the Maxwell Effect Gate public preview.

This module intentionally implements a small public-safe policy language.
It demonstrates branching, fail-closed behavior, inspectable reason codes,
YAML-held trust roots, and a readable condition list without disclosing
Maxwell private governance logic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from maxwell_effect_gate.effect_gate import GateDecision

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = ROOT_DIR / "policies" / "public_change_control_policy.yml"
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PolicyEvaluation:
    decision: GateDecision
    policy_id: str
    policy_version: str
    matched_rule_id: str


def load_policy(path: Path | str = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    """Load the public YAML policy file."""

    policy_path = Path(path)
    with policy_path.open("r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}
    if not isinstance(loaded, dict):
        raise ValueError("Policy file must load to a mapping.")
    return loaded


def required_public_input_fields(group_name: str, policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return required public-input fields for a policy input group."""

    loaded_policy = dict(policy or load_policy())
    fields = loaded_policy.get("required_public_inputs", {}).get(group_name, [])
    return [str(field) for field in fields]

def required_evidence_fields(policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return evidence fields required by the public policy."""

    return required_public_input_fields("evidence_bundle", policy)


def validate_evidence_bundle_shape(
    evidence_bundle: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[str]:
    """Return public-safe evidence-bundle shape errors.

    This helper lives in the policy engine so evidence requirements and
    malformed-input handling have one runtime source of truth.
    """

    loaded_policy = dict(policy or load_policy())
    errors = _missing_required_field_errors(
        group_name="evidence_bundle",
        group=evidence_bundle,
        required_fields=loaded_policy.get("required_public_inputs", {}).get(
            "evidence_bundle", []
        ),
    )
    errors.extend(_evidence_type_errors(evidence_bundle))
    return errors


def public_input_validation_errors(
    action_proposal: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any],
    authority_context: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[str]:
    """Return public-safe shape errors across action, evidence, and authority.

    The policy engine uses this as its canonical malformed-input check. The
    public proof intentionally validates only the interface shape exposed in
    ``policies/public_change_control_policy.yml``; deeper Maxwell authority and
    evidence logic remains outside the public-preview claim boundary.
    """

    loaded_policy = dict(policy or load_policy())
    required = loaded_policy.get("required_public_inputs", {})
    groups = {
        "action_proposal": action_proposal,
        "evidence_bundle": evidence_bundle,
        "authority_context": authority_context,
    }
    errors: list[str] = []

    for group_name, fields in required.items():
        group = groups.get(group_name, {})
        if not isinstance(group, Mapping):
            errors.append(f"INVALID_PUBLIC_INPUT_GROUP:{group_name}")
            continue
        errors.extend(
            _missing_required_field_errors(
                group_name=group_name,
                group=group,
                required_fields=fields or [],
            )
        )

    errors.extend(_evidence_type_errors(evidence_bundle))
    return errors


def _missing_required_field_errors(
    *, group_name: str, group: Mapping[str, Any], required_fields: Sequence[Any]
) -> list[str]:
    prefix = {
        "action_proposal": "MISSING_ACTION_FIELD",
        "evidence_bundle": "MISSING_EVIDENCE_FIELD",
        "authority_context": "MISSING_AUTHORITY_FIELD",
    }.get(group_name, "MISSING_PUBLIC_INPUT_FIELD")

    errors: list[str] = []
    for field in required_fields:
        field_name = str(field)
        value = group.get(field_name)
        if value is None or value == "" or value == [] or value == {}:
            errors.append(f"{prefix}:{field_name}")
    return errors


def _evidence_type_errors(evidence_bundle: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if "supporting_artifacts" in evidence_bundle and not isinstance(
        evidence_bundle["supporting_artifacts"], list
    ):
        errors.append("INVALID_EVIDENCE_FIELD:supporting_artifacts")
    if "limitations" in evidence_bundle and not isinstance(
        evidence_bundle["limitations"], list
    ):
        errors.append("INVALID_EVIDENCE_FIELD:limitations")
    return errors



def evaluate_policy(
    action_proposal: Mapping[str, Any] | None,
    evidence_bundle: Mapping[str, Any] | None,
    authority_context: Mapping[str, Any] | None,
    policy: Mapping[str, Any] | None = None,
) -> PolicyEvaluation:
    """Evaluate public inputs against the branching policy.

    Fail-closed invariant: anything malformed, missing, stale, unauthorized,
    contradictory, or out of scope must not be allowed.
    """

    loaded_policy = dict(policy or load_policy())
    policy_id = str(loaded_policy.get("policy_id", "unknown_policy"))
    policy_version = str(loaded_policy.get("version", "unknown_version"))

    action = _as_mapping(action_proposal)
    evidence = _as_mapping(evidence_bundle)
    authority = _as_mapping(authority_context)

    for rule in loaded_policy.get("rules", []):
        if not isinstance(rule, Mapping):
            continue
        if _rule_matches(rule.get("when", []), action, evidence, authority, loaded_policy):
            decision = str(rule.get("decision", loaded_policy.get("default_decision", "block")))
            if decision not in {"allow", "pause", "block"}:
                decision = "block"
            return PolicyEvaluation(
                decision=GateDecision(
                    decision=decision,
                    reason_codes=list(rule.get("reason_codes") or ["POLICY_RULE_MATCHED"]),
                    downstream_effect_allowed=(decision == "allow"),
                ),
                policy_id=policy_id,
                policy_version=policy_version,
                matched_rule_id=str(rule.get("id", "unnamed_rule")),
            )

    return PolicyEvaluation(
        decision=GateDecision(
            decision="block",
            reason_codes=["NO_MATCHING_POLICY_BRANCH", "NO_EFFECT_DEFAULT_BLOCK"],
            downstream_effect_allowed=False,
        ),
        policy_id=policy_id,
        policy_version=policy_version,
        matched_rule_id="default_block",
    )


def _as_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _rule_matches(
    conditions: Any,
    action: Mapping[str, Any],
    evidence: Mapping[str, Any],
    authority: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    """Return True only when every explicit condition matches."""

    if not isinstance(conditions, Sequence) or isinstance(conditions, (str, bytes)):
        return False

    for condition in conditions:
        if not _condition_matches(condition, action, evidence, authority, policy):
            return False

    return True


def _condition_matches(
    condition: Any,
    action: Mapping[str, Any],
    evidence: Mapping[str, Any],
    authority: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    if not isinstance(condition, Mapping):
        return False

    if "predicate" in condition:
        return _predicate_matches(
            str(condition.get("predicate")),
            action=action,
            evidence=evidence,
            authority=authority,
            policy=policy,
        )

    field_name = condition.get("field")
    operator = condition.get("op")
    if not isinstance(field_name, str) or not isinstance(operator, str):
        LOGGER.warning("Policy condition ignored because field/op is malformed: %r", condition)
        return False

    actual = _field_value(field_name, action, evidence, authority)
    expected = condition.get("value")

    if operator == "equals":
        return _strict_equals(actual, expected)
    if operator == "not_equals":
        return not _strict_equals(actual, expected)
    if operator == "in":
        return any(_strict_equals(actual, item) for item in _as_list(expected))
    if operator == "contains":
        return any(_strict_equals(item, expected) for item in _as_list(actual))
    if operator == "intersects":
        return bool(_strict_fingerprint_set(actual).intersection(_strict_fingerprint_set(expected)))

    LOGGER.warning("Unknown policy operator ignored fail-closed: %s", operator)
    return False


def _predicate_matches(
    predicate: str,
    *,
    action: Mapping[str, Any],
    evidence: Mapping[str, Any],
    authority: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    predicates = {
        "any_malformed_public_input": lambda: _any_malformed_public_input(
            action, evidence, authority, policy
        ),
        "any_missing_required_input": lambda: _any_malformed_public_input(
            action, evidence, authority, policy
        ),
        "action_type_not_in_allowed_values": lambda: action.get("action_type")
        not in _as_list(policy.get("allowed_values", {}).get("action_type")),
        "issuer_or_audience_untrusted": lambda: not _issuer_and_audience_trusted(
            authority, policy
        ),
        "issuer_and_audience_trusted": lambda: _issuer_and_audience_trusted(
            authority, policy
        ),
        "authority_expired": lambda: _authority_expired(authority.get("expires_at")),
        "requester_equals_approver": lambda: bool(action.get("requester_id"))
        and action.get("requester_id") == action.get("approver_id"),
        "subject_matches_requester": lambda: authority.get("subject")
        == action.get("requester_id"),
    }

    predicate_fn = predicates.get(predicate)
    if predicate_fn is None:
        LOGGER.warning("Unknown policy predicate ignored fail-closed: %s", predicate)
        return False
    return bool(predicate_fn())


def _field_value(
    dotted_name: str,
    action: Mapping[str, Any],
    evidence: Mapping[str, Any],
    authority: Mapping[str, Any],
) -> Any:
    namespaces = {
        "action": action,
        "evidence": evidence,
        "authority": authority,
    }
    namespace, _, key = dotted_name.partition(".")
    if not namespace or not key:
        return None
    source = namespaces.get(namespace)
    if source is None:
        return None
    return source.get(key)


def _any_malformed_public_input(
    action: Mapping[str, Any],
    evidence: Mapping[str, Any],
    authority: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    return bool(public_input_validation_errors(action, evidence, authority, policy))


def _issuer_and_audience_trusted(
    authority: Mapping[str, Any], policy: Mapping[str, Any]) -> bool:
    trust_roots = policy.get("trust_roots", {})
    trusted_issuers = _as_list(trust_roots.get("trusted_issuers"))
    expected_audiences = _as_list(trust_roots.get("expected_audiences"))
    issuer = authority.get("issuer")
    audiences = _strict_fingerprint_set(authority.get("audience"))
    expected_audience_fingerprints = _strict_fingerprint_set(expected_audiences)
    issuer_trusted = any(_strict_equals(issuer, trusted) for trusted in trusted_issuers)

    return bool(issuer_trusted and audiences.intersection(expected_audience_fingerprints))


def _authority_expired(expires_at: Any) -> bool:
    if not isinstance(expires_at, str) or not expires_at.strip():
        return True
    try:
        normalized = expires_at.replace("Z", "+00:00")
        expiry = datetime.fromisoformat(normalized)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    return expiry <= datetime.now(timezone.utc)


def _strict_equals(actual: Any, expected: Any) -> bool:
    """Return True only for exact value and exact public-input type matches."""

    return type(actual) is type(expected) and actual == expected


def _strict_fingerprint_set(value: Any) -> set[tuple[type[Any], Any]]:
    """Return type-aware fingerprints for hashable public-input values.

    Python considers ``1 == True``. Policy matching cannot, because hostile JSON
    inputs can use type coercion to smuggle booleans, scopes, or thresholds.
    Unhashable nested JSON values are dropped fail-closed.
    """

    safe: set[tuple[type[Any], Any]] = set()
    for item in _as_list(value):
        try:
            hash(item)
        except TypeError:
            continue
        safe.add((type(item), item))
    return safe


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    if value is None:
        return []
    return [value]
