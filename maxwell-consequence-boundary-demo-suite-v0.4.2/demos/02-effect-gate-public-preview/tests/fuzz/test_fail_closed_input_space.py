"""Expanded fail-closed input-space tests for the flagship public preview.

These tests are dependency-light on purpose. They complement the Hypothesis
property tests and run in the bounded mutation-smoke harness without requiring
third-party mutation tooling.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from maxwell_effect_gate.policy_engine import evaluate_policy, load_policy
from tests.test_policy_engine import valid_action, valid_authority, valid_evidence

REQUIRED_SCOPE = "change_record:create:staging"
VALID_ROLES = {"change_manager", "security_lead"}
TRUSTED_ISSUER = "https://issuer.example.test"
EXPECTED_AUDIENCE = "maxwell-effect-gate-public-proof"
POLICY = load_policy()

EDGE_VALUES: list[Any] = [
    None,
    "",
    " ",
    [],
    {},
    True,
    False,
    0,
    -1,
    1,
    1.0,
    1e308,
    float("inf"),
    float("-inf"),
    float("nan"),
    "true",
    "false",
    "staging\u202eproduction",
    "change_record:create:staging-extra",
    "CHANGE_RECORD:CREATE:STAGING",
    {"nested": {"value": "unexpected"}},
    ["change_record:create:staging-extra"],
]

ACTION_FIELDS = [
    "action_type",
    "target_environment",
    "risk_level",
    "requester_id",
    "approver_id",
    "dual_control_present",
]
EVIDENCE_FIELDS = [
    "evidence_bundle_id",
    "evidence_type",
    "source_workflow",
    "target_system",
    "cve_id",
    "research_summary",
    "supporting_artifacts",
    "limitations",
]
AUTHORITY_FIELDS = [
    "subject",
    "issuer",
    "audience",
    "expires_at",
    "scopes",
    "roles",
    "oauth_status",
]


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


def _present(value: Any) -> bool:
    if value in (None, "", [], {}):
        return False
    return True


def _not_expired(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        normalized = value.replace("Z", "+00:00")
        expiry = datetime.fromisoformat(normalized)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return expiry > datetime.now(timezone.utc)


def _contains_exact(items: Any, expected: Any) -> bool:
    return any(type(item) is type(expected) and item == expected for item in _as_list(items))


def _intersects(items: Any, expected: set[Any]) -> bool:
    for item in _as_list(items):
        try:
            if item in expected:
                return True
        except TypeError:
            continue
    return False


def _evidence_complete(evidence: Mapping[str, Any]) -> bool:
    if not all(_present(evidence.get(field)) for field in EVIDENCE_FIELDS):
        return False
    if not isinstance(evidence.get("supporting_artifacts"), list):
        return False
    if not isinstance(evidence.get("limitations"), list):
        return False
    return True


def _authority_valid(action: Mapping[str, Any], authority: Mapping[str, Any]) -> bool:
    return (
        authority.get("oauth_status") == "complete"
        and authority.get("subject") == action.get("requester_id")
        and authority.get("issuer") == TRUSTED_ISSUER
        and _contains_exact(authority.get("audience"), EXPECTED_AUDIENCE)
        and _contains_exact(authority.get("scopes"), REQUIRED_SCOPE)
        and _intersects(authority.get("roles"), VALID_ROLES)
        and _not_expired(authority.get("expires_at"))
    )


def _action_in_scope(action: Mapping[str, Any]) -> bool:
    return (
        action.get("action_type") == "create_change_control_record"
        and action.get("target_environment") == "staging"
        and action.get("risk_level") in {"low", "medium"}
        and action.get("dual_control_present") is True
        and bool(action.get("requester_id"))
        and action.get("requester_id") != action.get("approver_id")
    )


def _assert_allow_implies_invariant(action: dict[str, Any], evidence: dict[str, Any], authority: dict[str, Any]) -> None:
    result = evaluate_policy(action, evidence, authority, policy=POLICY)
    if result.decision.downstream_effect_allowed:
        assert result.decision.decision == "allow"
        assert _action_in_scope(action)
        assert _evidence_complete(evidence)
        assert _authority_valid(action, authority)


def _random_edge_value(rng: random.Random) -> Any:
    value = rng.choice(EDGE_VALUES)
    if isinstance(value, float) and math.isnan(value):
        return float("nan")
    if isinstance(value, (dict, list)):
        # Keep independent mutable instances between iterations.
        return value.copy()
    return value


def test_seeded_input_space_fuzz_allow_implies_fail_closed_invariant() -> None:
    rng = random.Random(20260314)

    for _ in range(120):
        action = valid_action()
        evidence = valid_evidence()
        authority = valid_authority()

        # Mutate a random number of fields across all three public inputs.
        for _ in range(rng.randint(1, 7)):
            group = rng.choice(["action", "evidence", "authority"])
            if group == "action":
                action[rng.choice(ACTION_FIELDS)] = _random_edge_value(rng)
            elif group == "evidence":
                evidence[rng.choice(EVIDENCE_FIELDS)] = _random_edge_value(rng)
            else:
                authority[rng.choice(AUTHORITY_FIELDS)] = _random_edge_value(rng)

        _assert_allow_implies_invariant(action, evidence, authority)


def test_parser_edge_values_fail_closed_without_exceptions() -> None:
    for field in ACTION_FIELDS:
        for value in EDGE_VALUES:
            action = valid_action()
            action[field] = value.copy() if isinstance(value, (dict, list)) else value
            result = evaluate_policy(action, valid_evidence(), valid_authority(), policy=POLICY)
            if field != "approver_id" or value != "different@example.test":
                assert result.decision.downstream_effect_allowed is False or _action_in_scope(action)

    for field in EVIDENCE_FIELDS:
        for value in EDGE_VALUES:
            evidence = valid_evidence()
            evidence[field] = value.copy() if isinstance(value, (dict, list)) else value
            result = evaluate_policy(valid_action(), evidence, valid_authority(), policy=POLICY)
            if not _evidence_complete(evidence):
                assert result.decision.downstream_effect_allowed is False

    for field in AUTHORITY_FIELDS:
        for value in EDGE_VALUES:
            authority = valid_authority()
            authority[field] = value.copy() if isinstance(value, (dict, list)) else value
            result = evaluate_policy(valid_action(), valid_evidence(), authority, policy=POLICY)
            if not _authority_valid(valid_action(), authority):
                assert result.decision.downstream_effect_allowed is False


def test_exact_threshold_and_type_confusion_cases_fail_closed_or_remain_bounded() -> None:
    cases = [
        (valid_action(risk_level="LOW"), valid_evidence(), valid_authority()),
        (valid_action(target_environment="staging "), valid_evidence(), valid_authority()),
        (valid_action(dual_control_present="true"), valid_evidence(), valid_authority()),
        (valid_action(), valid_evidence(supporting_artifacts="action_proposal.json"), valid_authority()),
        (valid_action(), valid_evidence(limitations="simulation"), valid_authority()),
        (valid_action(), valid_evidence(), valid_authority(scopes=["read:only", "change_record:create:staging-extra"])),
        (valid_action(), valid_evidence(), valid_authority(roles=["change_manager_assistant"])),
        (valid_action(), valid_evidence(), valid_authority(audience=["maxwell-effect-gate-public-proof-extra"])),
        (
            valid_action(),
            valid_evidence(),
            valid_authority(expires_at=(datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()),
        ),
    ]

    for action, evidence, authority in cases:
        result = evaluate_policy(action, evidence, authority, policy=POLICY)
        assert result.decision.downstream_effect_allowed is False
