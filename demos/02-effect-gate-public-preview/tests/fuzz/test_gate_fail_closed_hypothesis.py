"""Property-based fail-closed tests for adversarial public inputs.

These tests run when Hypothesis is installed through ``pip install -e \".[dev]\"``.
If a reviewer intentionally runs without dev dependencies, pytest reports them
as skipped rather than failing at import time.
"""

from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

given = hypothesis.given
settings = hypothesis.settings

from maxwell_effect_gate.policy_engine import evaluate_policy  # noqa: E402
from tests.test_policy_engine import valid_action, valid_authority, valid_evidence  # noqa: E402

REQUIRED_SCOPE = "change_record:create:staging"
VALID_ROLES = {"change_manager", "security_lead"}

json_leaf = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-10**9, max_value=10**9),
    st.floats(allow_nan=False, allow_infinity=False, width=32),
    st.text(min_size=0, max_size=50),
)
json_value = st.recursive(
    json_leaf,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(st.text(min_size=0, max_size=30), children, max_size=4),
    ),
    max_leaves=8,
)

scope_lists_without_required_scope = st.lists(
    st.text(min_size=0, max_size=40),
    max_size=5,
).filter(lambda scopes: REQUIRED_SCOPE not in scopes)

role_lists_without_valid_role = st.lists(
    st.text(min_size=0, max_size=40),
    max_size=5,
).filter(lambda roles: not set(roles).intersection(VALID_ROLES))

non_allow_environments = st.text(min_size=0, max_size=30).filter(lambda value: value != "staging")
non_allow_risks = st.text(min_size=0, max_size=30).filter(lambda value: value not in {"low", "medium"})
public_input_dicts = st.dictionaries(st.text(min_size=0, max_size=30), json_value, max_size=10)


@settings(max_examples=100)
@given(scopes=scope_lists_without_required_scope)
def test_no_authority_without_required_scope_can_allow(scopes):
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(scopes=scopes),
    )

    assert result.decision.decision in {"pause", "block"}
    assert result.decision.downstream_effect_allowed is False


@settings(max_examples=100)
@given(roles=role_lists_without_valid_role)
def test_no_authority_without_required_role_can_allow(roles):
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(roles=roles),
    )

    assert result.decision.decision in {"pause", "block"}
    assert result.decision.downstream_effect_allowed is False


@settings(max_examples=100)
@given(environment=non_allow_environments)
def test_non_staging_environment_never_allows(environment):
    result = evaluate_policy(
        valid_action(target_environment=environment),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision in {"pause", "block"}
    assert result.decision.downstream_effect_allowed is False


@settings(max_examples=100)
@given(risk=non_allow_risks)
def test_risk_outside_low_medium_never_allows(risk):
    result = evaluate_policy(
        valid_action(risk_level=risk),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision in {"pause", "block"}
    assert result.decision.downstream_effect_allowed is False


@settings(max_examples=100)
@given(status=st.text(min_size=0, max_size=30).filter(lambda value: value != "complete"))
def test_oauth_status_other_than_complete_never_allows(status):
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(oauth_status=status),
    )

    assert result.decision.decision == "block"
    assert result.decision.downstream_effect_allowed is False


@settings(max_examples=150)
@given(action=public_input_dicts, evidence=public_input_dicts, authority=public_input_dicts)
def test_arbitrary_public_input_shapes_do_not_raise_and_do_not_default_allow(action, evidence, authority):
    result = evaluate_policy(action, evidence, authority)
    if result.decision.downstream_effect_allowed:
        assert result.decision.decision == "allow"
        assert action.get("action_type") == "create_change_control_record"
        assert action.get("target_environment") == "staging"
        assert action.get("risk_level") in {"low", "medium"}
        assert action.get("dual_control_present") is True
        assert authority.get("oauth_status") == "complete"
        assert REQUIRED_SCOPE in authority.get("scopes", [])
        assert set(authority.get("roles", [])).intersection(VALID_ROLES)
