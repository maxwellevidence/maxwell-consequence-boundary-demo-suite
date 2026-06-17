"""Dependency-light adversarial bad-input matrix for public inputs."""

import itertools

from maxwell_effect_gate.policy_engine import evaluate_policy
from tests.test_policy_engine import valid_action, valid_authority, valid_evidence

BAD_VALUES = [None, "", [], {}, "production", "admin", True, False, 0, 999]


def test_authority_field_mutations_fail_closed_unless_exactly_authorized():
    required_authority_fields = [
        "subject",
        "issuer",
        "audience",
        "expires_at",
        "scopes",
        "roles",
        "oauth_status",
    ]

    for field, bad_value in itertools.product(required_authority_fields, BAD_VALUES):
        authority = valid_authority()
        authority[field] = bad_value
        result = evaluate_policy(valid_action(), valid_evidence(), authority)

        assert result.decision.decision in {"pause", "block"}
        assert result.decision.downstream_effect_allowed is False


def test_action_field_mutations_fail_closed_unless_exactly_bounded():
    mutations = {
        "action_type": [None, "", "delete_database", "approve_anything"],
        "target_environment": [None, "", "production", "prod", "staging\u202eproduction"],
        "risk_level": [None, "", "high", "critical", "unknown"],
        "requester_id": [None, ""],
        "approver_id": [None, ""],
        "dual_control_present": [None, "", False, "true"],
    }

    for field, values in mutations.items():
        for bad_value in values:
            action = valid_action()
            action[field] = bad_value
            result = evaluate_policy(action, valid_evidence(), valid_authority())

            assert result.decision.decision in {"pause", "block"}
            assert result.decision.downstream_effect_allowed is False


def test_evidence_field_mutations_fail_closed():
    required_evidence_fields = [
        "evidence_bundle_id",
        "evidence_type",
        "source_workflow",
        "target_system",
        "cve_id",
        "research_summary",
        "supporting_artifacts",
        "limitations",
    ]

    for field, bad_value in itertools.product(required_evidence_fields, [None, "", [], {}]):
        evidence = valid_evidence()
        evidence[field] = bad_value
        result = evaluate_policy(valid_action(), evidence, valid_authority())

        assert result.decision.decision == "block"
        assert result.decision.downstream_effect_allowed is False
