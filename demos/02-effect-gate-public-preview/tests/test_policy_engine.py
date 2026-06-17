"""Reviewer-facing policy-engine tests for fail-closed behavior."""

import logging
from datetime import datetime, timedelta, timezone

from maxwell_effect_gate.policy_engine import evaluate_policy, load_policy


def valid_action(**overrides):
    action = {
        "action_type": "create_change_control_record",
        "target_environment": "staging",
        "risk_level": "low",
        "requester_id": "requester@example.test",
        "approver_id": "approver@example.test",
        "dual_control_present": True,
    }
    action.update(overrides)
    return action


def valid_evidence(**overrides):
    evidence = {
        "evidence_bundle_id": "EVID-001",
        "evidence_type": "simulated_cve_remediation_research",
        "source_workflow": "ai_assisted_cve_incident_research",
        "target_system": "payments-api",
        "cve_id": "CVE-2026-1043",
        "research_summary": "Simulated public-safe remediation research.",
        "supporting_artifacts": ["action_proposal.json"],
        "limitations": ["simulation"],
    }
    evidence.update(overrides)
    return evidence


def valid_authority(**overrides):
    authority = {
        "subject": "requester@example.test",
        "issuer": "https://issuer.example.test",
        "audience": "maxwell-effect-gate-public-proof",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "scopes": ["change_record:create:staging"],
        "roles": ["change_manager"],
        "oauth_status": "complete",
    }
    authority.update(overrides)
    return authority


def test_policy_file_loads_and_declares_default_block_and_trust_roots():
    policy = load_policy()
    assert policy["policy_id"] == "maxwell.public.change_control.v0_3"
    assert policy["version"] == "0.3.0"
    assert policy["default_decision"] == "block"
    assert policy["effect_boundary"] == "change_control_record_creation"
    assert policy["condition_language"] == "public_condition_list_v1"
    assert policy["trust_roots"]["trusted_issuers"] == ["https://issuer.example.test"]
    assert policy["trust_roots"]["expected_audiences"] == ["maxwell-effect-gate-public-proof"]


def test_complete_staging_low_change_is_allowed():
    result = evaluate_policy(valid_action(), valid_evidence(), valid_authority())

    assert result.decision.decision == "allow"
    assert result.decision.downstream_effect_allowed is True
    assert result.matched_rule_id == "allow_staging_low_or_medium_with_complete_authority"


def test_boundary_staging_medium_with_dual_control_is_allowed():
    result = evaluate_policy(
        valid_action(risk_level="medium"),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision == "allow"
    assert result.matched_rule_id == "allow_staging_low_or_medium_with_complete_authority"


def test_boundary_staging_high_with_dual_control_defaults_to_block():
    result = evaluate_policy(
        valid_action(risk_level="high"),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision == "block"
    assert result.decision.downstream_effect_allowed is False
    assert result.matched_rule_id == "default_block"
    assert "NO_EFFECT_DEFAULT_BLOCK" in result.decision.reason_codes


def test_boundary_production_low_with_dual_control_defaults_to_block():
    result = evaluate_policy(
        valid_action(target_environment="production", risk_level="low"),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision == "block"
    assert result.decision.downstream_effect_allowed is False
    assert result.matched_rule_id == "default_block"


def test_unknown_action_type_blocks():
    result = evaluate_policy(
        valid_action(action_type="create_prod_backdoor"),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision == "block"
    assert "UNKNOWN_ACTION_TYPE" in result.decision.reason_codes


def test_missing_evidence_blocks_before_authority_can_allow():
    result = evaluate_policy(
        valid_action(),
        valid_evidence(research_summary=""),
        valid_authority(),
    )

    assert result.decision.decision == "block"
    assert "MALFORMED_PUBLIC_INPUT" in result.decision.reason_codes


def test_expired_authority_blocks():
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(expires_at="2020-01-01T00:00:00Z"),
    )

    assert result.decision.decision == "block"
    assert "AUTHORITY_CONTEXT_EXPIRED" in result.decision.reason_codes


def test_self_approval_blocks():
    result = evaluate_policy(
        valid_action(approver_id="requester@example.test"),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision == "block"
    assert "SELF_APPROVAL_NOT_PERMITTED" in result.decision.reason_codes


def test_staging_missing_dual_control_pauses_not_allows():
    result = evaluate_policy(
        valid_action(dual_control_present=False),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision == "pause"
    assert result.decision.downstream_effect_allowed is False
    assert "HUMAN_APPROVAL_REQUIRED" in result.decision.reason_codes


def test_production_high_risk_without_dual_control_blocks():
    result = evaluate_policy(
        valid_action(
            target_environment="production",
            risk_level="critical",
            dual_control_present=False,
        ),
        valid_evidence(),
        valid_authority(),
    )

    assert result.decision.decision == "block"
    assert "PRODUCTION_HIGH_RISK_REQUIRES_DUAL_CONTROL" in result.decision.reason_codes


def test_missing_scope_blocks_by_default_no_allow():
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(scopes=["read:only"]),
    )

    assert result.decision.decision == "block"
    assert result.decision.downstream_effect_allowed is False
    assert result.matched_rule_id == "default_block"


def test_invalid_issuer_blocks_from_yaml_trust_roots():
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(issuer="https://evil.example.test"),
    )

    assert result.decision.decision == "block"
    assert "INVALID_ISSUER_OR_AUDIENCE" in result.decision.reason_codes


def test_invalid_audience_blocks_from_yaml_trust_roots():
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(audience="wrong-audience"),
    )

    assert result.decision.decision == "block"
    assert "INVALID_ISSUER_OR_AUDIENCE" in result.decision.reason_codes


def test_subject_mismatch_blocks_by_default_no_allow():
    result = evaluate_policy(
        valid_action(requester_id="other@example.test"),
        valid_evidence(),
        valid_authority(subject="requester@example.test"),
    )

    assert result.decision.decision == "block"
    assert result.decision.downstream_effect_allowed is False
    assert result.matched_rule_id == "default_block"


def test_invalid_oauth_status_blocks_before_allow():
    result = evaluate_policy(
        valid_action(),
        valid_evidence(),
        valid_authority(oauth_status="invalid"),
    )

    assert result.decision.decision == "block"
    assert "INVALID_OR_ABSENT_OAUTH_CONTEXT" in result.decision.reason_codes


def test_unknown_policy_predicate_warns_and_fails_closed(caplog):
    policy = {
        "policy_id": "test.policy",
        "version": "test",
        "default_decision": "block",
        "rules": [
            {
                "id": "allow_with_typo_predicate",
                "decision": "allow",
                "when": [{"predicate": "typo_predicate"}],
            }
        ],
    }

    with caplog.at_level(logging.WARNING):
        result = evaluate_policy(valid_action(), valid_evidence(), valid_authority(), policy)

    assert result.decision.decision == "block"
    assert result.matched_rule_id == "default_block"
    assert any("Unknown policy predicate" in record.message for record in caplog.records)


def test_unknown_policy_operator_warns_and_fails_closed(caplog):
    policy = {
        "policy_id": "test.policy",
        "version": "test",
        "default_decision": "block",
        "rules": [
            {
                "id": "allow_with_typo_operator",
                "decision": "allow",
                "when": [
                    {
                        "field": "action.target_environment",
                        "op": "equals_typo",
                        "value": "staging",
                    }
                ],
            }
        ],
    }

    with caplog.at_level(logging.WARNING):
        result = evaluate_policy(valid_action(), valid_evidence(), valid_authority(), policy)

    assert result.decision.decision == "block"
    assert result.matched_rule_id == "default_block"
    assert any("Unknown policy operator" in record.message for record in caplog.records)
