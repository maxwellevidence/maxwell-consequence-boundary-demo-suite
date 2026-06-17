"""Tests for the public Maxwell Effect Gate proof."""

import base64
import json
import shutil
import time

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from maxwell_effect_gate.policy_engine import (
    required_evidence_fields,
    validate_evidence_bundle_shape,
)
from maxwell_effect_gate.run_demo import (
    ARTIFACTS_DIR,
    EXAMPLES_DIR,
    ROOT_DIR,
    VALID_CASES,
    load_demo_input,
    main,
    run_case,
)
from maxwell_effect_gate.hashing import sha256_file
from maxwell_effect_gate.verify_artifacts import verify_run

EXPECTED_DECISIONS = {
    "staging_low_risk_dual_control": "allow",
    "staging_missing_dual_control": "pause",
    "production_critical_no_dual_control": "block",
    "expired_authority": "block",
    "self_approval": "block",
    "oidc_signed_token": "allow",
    "malformed_evidence_missing_field": "block",
    "oidc_bad_token_wrong_audience": "block",
    "oidc_bad_token_bad_signature": "block",
    "oidc_bad_token_expired": "block",
    "oidc_bad_token_missing_scope": "block",
}

COMMON_ARTIFACTS = {
    "action_proposal.json",
    "evidence_bundle.json",
    "authority_context.json",
    "workflow_output.json",
    "decision_surface_output.json",
    "decision_receipt.json",
    "config_original.yml",
    "config_effective.yml",
    "workflow_profiling_metrics.json",
    "replay_manifest.json",
    "artifact_hashes.sha256.txt",
    "artifact_hashes.sha256.txt.sig",
}


def reset_artifacts() -> None:
    """Remove generated run folders while preserving package README/sample outputs."""

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        for child in ARTIFACTS_DIR.iterdir():
            if child.is_dir() and child.name.endswith("_run"):
                shutil.rmtree(child, ignore_errors=True)
        time.sleep(0.05)
    for child in ARTIFACTS_DIR.iterdir():
        if child.is_dir() and child.name.endswith("_run"):
            shutil.rmtree(child)


def receipt_for(case: str) -> dict:
    path = ARTIFACTS_DIR / f"{case}_run" / "decision_receipt.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_demo_cases_are_shape_named_and_inputs_have_no_outcome_label():
    assert "allow" not in VALID_CASES
    assert "pause" not in VALID_CASES
    assert "block" not in VALID_CASES

    for case in [case for case in VALID_CASES if not case.startswith("oidc_")]:
        demo_input = load_demo_input(case)
        assert "case" not in demo_input
        assert "decision" not in demo_input
        assert "action_proposal" in demo_input
        assert "authority_context" in demo_input


def test_policy_derived_allow_creates_effect_records_but_pause_and_block_do_not():
    reset_artifacts()
    main([])

    for case, expected_decision in EXPECTED_DECISIONS.items():
        run_dir = ARTIFACTS_DIR / f"{case}_run"
        receipt = receipt_for(case)

        assert receipt["decision"] == expected_decision
        assert receipt["matched_policy_rule_id"]
        assert receipt["policy_id"] == "maxwell.public.change_control.v0_3"
        assert receipt["policy_version"] == "0.3.0"

        if expected_decision == "allow":
            assert (run_dir / "effect_record.json").exists()
            assert not (run_dir / "interaction_or_oauth_required.json").exists()
        elif expected_decision == "pause":
            assert not (run_dir / "effect_record.json").exists()
            assert (run_dir / "interaction_or_oauth_required.json").exists()
        else:
            assert not (run_dir / "effect_record.json").exists()
            assert not (run_dir / "interaction_or_oauth_required.json").exists()


def test_all_runs_emit_artifact_chain_and_signed_manifest():
    reset_artifacts()
    main([])

    for case in VALID_CASES:
        run_dir = ARTIFACTS_DIR / f"{case}_run"
        existing = {path.name for path in run_dir.iterdir() if path.is_file()}
        assert COMMON_ARTIFACTS.issubset(existing)

        manifest_text = (run_dir / "artifact_hashes.sha256.txt").read_text(encoding="utf-8")
        assert "action_proposal.json" in manifest_text
        assert "evidence_bundle.json" in manifest_text
        assert "authority_context.json" in manifest_text
        assert "decision_receipt.json" in manifest_text
        assert "config_original.yml" in manifest_text
        assert "config_effective.yml" in manifest_text

        errors = verify_run(f"{case}_run")
        assert errors == []


def test_oidc_demo_cases_surface_validation_result_without_token_material():
    reset_artifacts()
    run_case("oidc_signed_token")
    run_case("oidc_bad_token_wrong_audience")
    run_case("oidc_bad_token_bad_signature")
    run_case("oidc_bad_token_expired")
    run_case("oidc_bad_token_missing_scope")

    good = json.loads(
        (ARTIFACTS_DIR / "oidc_signed_token_run" / "oidc_validation_result.json").read_text(
            encoding="utf-8"
        )
    )
    bad_cases = [
        "oidc_bad_token_wrong_audience",
        "oidc_bad_token_bad_signature",
        "oidc_bad_token_expired",
        "oidc_bad_token_missing_scope",
    ]
    bad_results = [
        json.loads(
            (ARTIFACTS_DIR / f"{case}_run" / "oidc_validation_result.json").read_text(
                encoding="utf-8"
            )
        )
        for case in bad_cases
    ]

    assert good["validation_valid"] is True
    assert good["issuer_public_key_source"] == "fixtures/oidc_demo_issuer_public_key.pem"
    assert good["token_material_written_to_artifacts"] is False
    assert receipt_for("oidc_signed_token")["decision"] == "allow"
    for case, result in zip(bad_cases, bad_results):
        assert result["validation_valid"] is False
        assert result["token_material_written_to_artifacts"] is False
        assert receipt_for(case)["decision"] == "block"


def test_malformed_evidence_demo_exercises_malformed_public_inputs_branch():
    reset_artifacts()
    run_case("malformed_evidence_missing_field")

    receipt = receipt_for("malformed_evidence_missing_field")

    assert receipt["decision"] == "block"
    assert receipt["matched_policy_rule_id"] == "block_malformed_public_inputs"
    assert "MALFORMED_PUBLIC_INPUT" in receipt["reason_codes"]


def test_verifier_detects_modified_artifact_after_manifest_written():
    reset_artifacts()
    run_case("staging_low_risk_dual_control")

    artifact_path = ARTIFACTS_DIR / "staging_low_risk_dual_control_run" / "decision_receipt.json"
    original_text = artifact_path.read_text(encoding="utf-8")
    artifact_path.write_text(
        original_text.replace('"decision": "allow"', '"decision": "tampered_allow"'),
        encoding="utf-8",
    )

    errors = verify_run("staging_low_risk_dual_control_run")

    assert any("hash mismatch for decision_receipt.json" in error for error in errors)


def test_verifier_detects_manifest_tampering_via_signature():
    reset_artifacts()
    run_case("staging_low_risk_dual_control")

    manifest_path = ARTIFACTS_DIR / "staging_low_risk_dual_control_run" / "artifact_hashes.sha256.txt"
    manifest_path.write_text(
        manifest_path.read_text(encoding="utf-8").replace("effect_record.json", "effect_record_tampered.json"),
        encoding="utf-8",
    )

    errors = verify_run("staging_low_risk_dual_control_run")

    assert any("manifest signature verification failed" in error for error in errors)


def test_verifier_rejects_run_directory_key_remint_attack():
    reset_artifacts()
    run_case("staging_low_risk_dual_control")

    run_dir = ARTIFACTS_DIR / "staging_low_risk_dual_control_run"
    artifact_path = run_dir / "action_proposal.json"
    artifact_path.write_text('{"tampered": true}\n', encoding="utf-8")

    manifest_path = run_dir / "artifact_hashes.sha256.txt"
    new_digest = sha256_file(artifact_path)
    rewritten_lines = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if line.endswith("  action_proposal.json"):
            rewritten_lines.append(f"{new_digest}  action_proposal.json")
        else:
            rewritten_lines.append(line)
    manifest_path.write_text("\n".join(rewritten_lines) + "\n", encoding="utf-8")

    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    signature = attacker_key.sign(
        manifest_path.read_bytes(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    (run_dir / "artifact_hashes.sha256.txt.sig").write_text(
        base64.b64encode(signature).decode("ascii") + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest_public_key.pem").write_bytes(
        attacker_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

    errors = verify_run("staging_low_risk_dual_control_run")

    assert any("manifest signature verification failed" in error for error in errors)


def test_verifier_detects_missing_expected_manifest_entry():
    reset_artifacts()
    run_case("staging_low_risk_dual_control")

    manifest_path = ARTIFACTS_DIR / "staging_low_risk_dual_control_run" / "artifact_hashes.sha256.txt"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    filtered_lines = [
        line
        for line in manifest_text.splitlines()
        if "effect_record.json" not in line
    ]
    manifest_path.write_text("\n".join(filtered_lines) + "\n", encoding="utf-8")

    errors = verify_run("staging_low_risk_dual_control_run")

    assert any("manifest missing effect_record.json" in error for error in errors)
    assert any("manifest signature verification failed" in error for error in errors)


def test_verifier_detects_improper_effect_record_after_pause_or_block():
    reset_artifacts()

    run_case("staging_missing_dual_control")
    pause_effect_record = ARTIFACTS_DIR / "staging_missing_dual_control_run" / "effect_record.json"
    pause_effect_record.write_text('{"status": "improperly_created_after_pause"}\n', encoding="utf-8")

    pause_errors = verify_run("staging_missing_dual_control_run")
    assert any("effect_record.json must not exist" in error for error in pause_errors)

    run_case("production_critical_no_dual_control")
    block_effect_record = ARTIFACTS_DIR / "production_critical_no_dual_control_run" / "effect_record.json"
    block_effect_record.write_text('{"status": "improperly_created_after_block"}\n', encoding="utf-8")

    block_errors = verify_run("production_critical_no_dual_control_run")
    assert any("effect_record.json must not exist" in error for error in block_errors)


def test_unknown_run_case_label_is_rejected():
    with pytest.raises(ValueError, match="Unknown case"):
        run_case("approve")


def test_incomplete_evidence_bundle_reports_missing_policy_fields():
    incomplete_evidence_bundle = {
        "evidence_bundle_id": "EVID-INCOMPLETE",
        "evidence_type": "simulated_cve_remediation_research",
    }

    errors = validate_evidence_bundle_shape(incomplete_evidence_bundle)

    assert "source_workflow" in required_evidence_fields()
    assert "MISSING_EVIDENCE_FIELD:source_workflow" in errors
    assert "MISSING_EVIDENCE_FIELD:target_system" in errors
    assert "MISSING_EVIDENCE_FIELD:cve_id" in errors
    assert "MISSING_EVIDENCE_FIELD:research_summary" in errors
    assert "MISSING_EVIDENCE_FIELD:supporting_artifacts" in errors
    assert "MISSING_EVIDENCE_FIELD:limitations" in errors


def test_invalid_evidence_bundle_list_fields_report_errors():
    invalid_evidence_bundle = {
        "evidence_bundle_id": "EVID-INVALID",
        "evidence_type": "simulated_cve_remediation_research",
        "source_workflow": "ai_assisted_cve_incident_research",
        "target_system": "payments-api",
        "cve_id": "CVE-2026-1043",
        "research_summary": "Simulated summary.",
        "supporting_artifacts": "action_proposal.json",
        "limitations": "not a list",
    }

    errors = validate_evidence_bundle_shape(invalid_evidence_bundle)

    assert "INVALID_EVIDENCE_FIELD:supporting_artifacts" in errors
    assert "INVALID_EVIDENCE_FIELD:limitations" in errors


def test_malformed_demo_input_json_file_is_rejected():
    malformed_path = EXAMPLES_DIR / "malformed_test.json"
    malformed_path.write_text('{"description": "broken",', encoding="utf-8")

    try:
        with pytest.raises(json.JSONDecodeError):
            load_demo_input("malformed_test")
    finally:
        malformed_path.unlink(missing_ok=True)


def test_version_file_matches_pyproject_version():
    version_text = (ROOT_DIR / "VERSION").read_text(encoding="utf-8").strip()
    pyproject_text = (ROOT_DIR / "pyproject.toml").read_text(encoding="utf-8")

    assert version_text.startswith("0.3.0")
    assert 'version = "0.3.0"' in pyproject_text


def test_run_demo_main_accepts_explicit_empty_argv():
    reset_artifacts()
    main([])

    for case in VALID_CASES:
        assert (ARTIFACTS_DIR / f"{case}_run").exists()
