from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

EXCLUDE_FROM_MANIFEST = {"manifest.json", "verification_report.json"}
EFFECT_FILE = "bounded_effect_record.json"
NO_EFFECT_FILE = "NO_BOUNDARY_EFFECT_CREATED.txt"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha_obj(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_policy(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Policy must be a mapping: {path}")
    data["_source_path"] = str(path)
    data["_policy_hash"] = sha_obj({k: v for k, v in data.items() if not k.startswith("_")})
    return data


def policy_snapshot(policy: dict[str, Any]) -> dict[str, Any]:
    public_policy = {k: v for k, v in policy.items() if not k.startswith("_")}
    return {
        "record_type": "policy_snapshot",
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "policy_hash": f"sha256:{policy['_policy_hash']}",
        "policy": public_policy,
    }


def risk_rank(policy: dict[str, Any], value: str | None) -> int:
    return int((policy.get("risk_order") or {}).get(str(value or "").lower(), 999))


def _text_blob(req: dict[str, Any]) -> str:
    llm = req.get("llm_output") or {}
    external = req.get("external_instruction") or {}
    action = req.get("proposed_action") or {}
    tool = req.get("tool_request") or {}
    parts = [
        external.get("text"),
        llm.get("recommendation"),
        llm.get("instruction_trace"),
        llm.get("tool_rationale"),
        action.get("description"),
        tool.get("rationale"),
    ]
    return " ".join(str(p or "") for p in parts).lower()


def approval_source_lists(req: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evidence = req.get("evidence") or {}
    llm = req.get("llm_output") or {}
    approvals = list(evidence.get("approvals") or [])
    llm_claims = [
        {"source": "llm_output", "approver_id": a.get("approver_id"), "approval_id": a.get("approval_id")}
        for a in list(llm.get("claimed_approvals") or [])
    ]
    return approvals, llm_claims


def prompt_boundary_analysis(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    action = req.get("proposed_action") or {}
    llm = req.get("llm_output") or {}
    tool = req.get("tool_request") or {}
    blob = _text_blob(req)
    indicators = [
        str(indicator)
        for indicator in policy.get("prompt_injection_indicators") or []
        if str(indicator).lower() in blob
    ]
    explicit_flag = bool(llm.get("prompt_injection_detected"))
    requested_tool = tool.get("tool_name") or action.get("tool_name")
    prohibited_tools = set(policy.get("prohibited_tools") or [])
    tool_prohibited = requested_tool in prohibited_tools
    tool_override_requested = bool(tool.get("override_safety") or llm.get("tool_override_requested"))
    approvals, llm_claims = approval_source_lists(req)
    untrusted_sources = set(policy.get("untrusted_authority_sources") or [])
    untrusted_claims = [
        item
        for item in approvals + llm_claims
        if item.get("source") in untrusted_sources or not item.get("source")
    ]
    declared = action.get("declared_risk_level") or action.get("risk_level")
    actual = action.get("risk_level")
    risk_downgrade = risk_rank(policy, declared) < risk_rank(policy, actual)
    if bool(llm.get("attempted_risk_downgrade")):
        risk_downgrade = True

    return {
        "record_type": "prompt_boundary_analysis",
        "case_id": req["case_id"],
        "prompt_injection_detected": explicit_flag or bool(indicators),
        "explicit_prompt_injection_flag": explicit_flag,
        "matched_indicators": sorted(set(indicators)),
        "instruction_trace_preserved": bool(llm.get("instruction_trace")),
        "requested_tool": requested_tool,
        "tool_prohibited": tool_prohibited,
        "tool_override_requested": tool_override_requested,
        "untrusted_authority_claims": untrusted_claims,
        "untrusted_authority_claim_present": bool(untrusted_claims),
        "declared_risk_level": declared,
        "evaluated_risk_level": actual,
        "risk_downgrade_attempt_detected": bool(risk_downgrade),
        "model_output_treated_as_authority": False,
    }


def required_refs_for_action(req: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    action = req.get("proposed_action") or {}
    refs = list(policy.get("base_required_evidence_refs") or [])
    if action.get("risk_level") in set(policy.get("review_required_risk_levels") or []):
        refs.extend(policy.get("high_risk_required_evidence_refs") or [])
    return sorted(set(refs))


def instruction_evidence_bundle(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    evidence = req.get("evidence") or {}
    llm = req.get("llm_output") or {}
    external = req.get("external_instruction") or {}
    refs = list(evidence.get("refs") or [])
    required = required_refs_for_action(req, policy)
    missing = sorted(set(required) - set(refs))
    return {
        "record_type": "instruction_evidence_bundle",
        "case_id": req["case_id"],
        "action_id": (req.get("proposed_action") or {}).get("action_id"),
        "evidence_refs": refs,
        "required_refs": required,
        "missing_refs": missing,
        "evidence_complete": not missing,
        "external_instruction_preserved": bool(external.get("text")),
        "llm_recommendation_preserved": bool(llm.get("recommendation")),
        "instruction_trace_preserved": bool(llm.get("instruction_trace")),
        "business_justification": evidence.get("business_justification"),
        "captured_at": evidence.get("captured_at"),
    }


def authority_context(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    actor = req.get("actor") or {}
    action = req.get("proposed_action") or {}
    tool = req.get("tool_request") or {}
    role = actor.get("role")
    role_profile = dict((policy.get("roles") or {}).get(role) or {})
    allowed_scopes = set(role_profile.get("allowed_scopes") or [])
    allowed_effect_types = set(role_profile.get("allowed_effect_types") or [])
    allowed_targets = set(role_profile.get("allowed_target_systems") or [])
    allowed_tools = set(role_profile.get("allowed_tools") or [])
    approvals, _llm_claims = approval_source_lists(req)
    trusted_sources = set(policy.get("trusted_authority_sources") or [])
    trusted_approvals = [a for a in approvals if a.get("source") in trusted_sources]
    self_approvals = [a for a in trusted_approvals if a.get("approver_id") == actor.get("actor_id")]
    requested_tool = tool.get("tool_name") or action.get("tool_name")
    return {
        "record_type": "authority_context",
        "case_id": req["case_id"],
        "actor_id": actor.get("actor_id"),
        "actor_role": role,
        "role_known": bool(role_profile),
        "can_propose_action": bool(role_profile.get("can_propose_action")),
        "effect_type": action.get("effect_type"),
        "effect_type_in_scope": action.get("effect_type") in allowed_effect_types,
        "scope": action.get("scope"),
        "scope_in_role_scope": action.get("scope") in allowed_scopes,
        "target_system": action.get("target_system"),
        "target_in_role_scope": action.get("target_system") in allowed_targets,
        "requested_tool": requested_tool,
        "tool_in_role_scope": requested_tool in allowed_tools if requested_tool else True,
        "risk_level": action.get("risk_level"),
        "max_risk_without_review": role_profile.get("max_risk_without_review"),
        "risk_exceeds_no_review_threshold": risk_rank(policy, action.get("risk_level"))
        > risk_rank(policy, role_profile.get("max_risk_without_review")),
        "trusted_approval_count": len(trusted_approvals),
        "trusted_approval_ids": [a.get("approval_id") for a in trusted_approvals],
        "self_approval_detected": bool(self_approvals),
        "authority_present": bool(role_profile.get("can_propose_action")),
    }


def _decision(
    name: str,
    lifecycle: str,
    permitted: bool,
    review_required: bool,
    quarantine_required: bool,
    code: str,
    explanation: str,
) -> dict[str, Any]:
    return {
        "decision": name,
        "lifecycle_status": lifecycle,
        "effect_permitted": permitted,
        "security_review_required": review_required,
        "quarantine_required": quarantine_required,
        "reason_code": code,
        "explanation": explanation,
    }


def evaluate(
    req: dict[str, Any],
    policy: dict[str, Any],
    ev: dict[str, Any],
    auth: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    reason = policy["reason_codes"]

    if boundary["prompt_injection_detected"]:
        return _decision(
            "quarantine",
            "prompt_quarantined_effect_suppressed",
            False,
            False,
            True,
            reason["prompt_injection_quarantined"],
            "Prompt-injected override language was preserved as evidence, not treated as authority.",
        )
    if boundary["tool_prohibited"] or boundary["tool_override_requested"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            False,
            reason["malicious_tool_request"],
            "The requested tool is outside the permitted consequence boundary.",
        )
    if boundary["untrusted_authority_claim_present"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            False,
            reason["untrusted_authority_claim"],
            "Authority claimed in model output or prompt text is not trusted authority.",
        )
    if boundary["risk_downgrade_attempt_detected"]:
        return _decision(
            "security_review",
            "security_review_routed",
            False,
            True,
            False,
            reason["risk_downgrade_review"],
            "The model attempted to relabel a higher-risk action as lower risk; no effect is created.",
        )
    if not auth["authority_present"] or not auth["role_known"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            False,
            reason["missing_authority"],
            "The actor does not have recognized authority to propose this effect.",
        )
    if not auth["effect_type_in_scope"] or not auth["scope_in_role_scope"] or not auth["target_in_role_scope"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            False,
            reason["scope_violation"],
            "The effect type, scope, or target system is outside actor authority.",
        )
    if not auth["tool_in_role_scope"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            False,
            reason["malicious_tool_request"],
            "The requested tool is not within the actor's permitted tool boundary.",
        )
    if auth["self_approval_detected"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            False,
            reason["untrusted_authority_claim"],
            "Self-approval is not sufficient authority for downstream effect in this demo.",
        )
    if not ev["evidence_complete"]:
        return _decision(
            "security_review",
            "security_review_routed",
            False,
            True,
            False,
            reason["missing_evidence_review"],
            "Required evidence is missing; the action is routed to security review without effect.",
        )
    if auth["risk_exceeds_no_review_threshold"]:
        return _decision(
            "security_review",
            "security_review_routed",
            False,
            True,
            False,
            reason["high_risk_review"],
            "The action exceeds the actor's no-review risk threshold.",
        )

    return _decision(
        "commit",
        "effect_committed",
        True,
        False,
        False,
        reason["effect_committed"],
        "Instruction evidence, actor authority, and tool boundary are sufficient for bounded effect.",
    )


def build_decision_receipt(
    req: dict[str, Any],
    policy: dict[str, Any],
    ev: dict[str, Any],
    auth: dict[str, Any],
    boundary: dict[str, Any],
    dec: dict[str, Any],
) -> dict[str, Any]:
    rec = {
        "record_type": "decision_receipt",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "policy_hash": f"sha256:{policy['_policy_hash']}",
        "evaluated_at": policy.get("evaluation_time"),
        "instruction_evidence_bundle_hash": f"sha256:{sha_obj(ev)}",
        "authority_context_hash": f"sha256:{sha_obj(auth)}",
        "prompt_boundary_analysis_hash": f"sha256:{sha_obj(boundary)}",
        **dec,
    }
    rec["decision_receipt_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_effect_record(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    action = req["proposed_action"]
    tool = req.get("tool_request") or {}
    rec = {
        "record_type": "bounded_effect_record",
        "case_id": req["case_id"],
        "action_id": action.get("action_id"),
        "effect_type": action.get("effect_type"),
        "scope": action.get("scope"),
        "target_system": action.get("target_system"),
        "tool_name": tool.get("tool_name") or action.get("tool_name"),
        "effect_payload": action.get("requested_change"),
        "effect_basis": receipt["decision_receipt_id"],
        "bounded_effect_committed": True,
        "note": "This synthetic demo records a bounded effect; it does not call downstream tools.",
    }
    rec["bounded_effect_record_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_security_review_ticket(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "security_review_ticket",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "review_queue": "prompt_boundary_security_review",
        "reason_code": receipt["reason_code"],
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["security_review_ticket_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_quarantine_ticket(req: dict[str, Any], receipt: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "quarantine_ticket",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "quarantine_queue": "prompt_injection_boundary_quarantine",
        "reason_code": receipt["reason_code"],
        "matched_indicators": boundary.get("matched_indicators") or [],
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["quarantine_ticket_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_suppression_notice(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "suppression_notice",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "reason_code": receipt["reason_code"],
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["suppression_notice_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def write_manifest(run_dir: Path) -> dict[str, Any]:
    files = []
    for p in sorted(run_dir.iterdir()):
        if p.is_file() and p.name not in EXCLUDE_FROM_MANIFEST:
            files.append({"path": p.name, "sha256": sha_file(p), "bytes": p.stat().st_size})
    man = {"record_type": "manifest", "case_id": run_dir.name, "files": files}
    write_json(run_dir / "manifest.json", man)
    return man


def verify_run(run_dir: Path, write_report: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        errors.append("manifest.json missing")
        manifest = {"files": []}
    else:
        manifest = read_json(manifest_path)
    checked = 0
    for item in manifest.get("files", []):
        p = run_dir / item["path"]
        if not p.exists():
            errors.append(f"missing file: {item['path']}")
            continue
        checked += 1
        if sha_file(p) != item["sha256"]:
            errors.append(f"hash mismatch: {item['path']}")

    receipt_path = run_dir / "decision_receipt.json"
    receipt = read_json(receipt_path) if receipt_path.exists() else {}
    if not receipt:
        errors.append("decision_receipt.json missing")
    effect_exists = (run_dir / EFFECT_FILE).exists()
    no_effect_exists = (run_dir / NO_EFFECT_FILE).exists()
    review_exists = (run_dir / "security_review_ticket.json").exists()
    quarantine_exists = (run_dir / "quarantine_ticket.json").exists()
    suppression_exists = (run_dir / "suppression_notice.json").exists()

    if receipt.get("effect_permitted") and not effect_exists:
        errors.append(f"{EFFECT_FILE} missing despite effect_permitted=true")
    if receipt.get("effect_permitted") and no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} exists despite effect_permitted=true")
    if not receipt.get("effect_permitted") and effect_exists:
        errors.append(f"{EFFECT_FILE} exists despite effect_permitted=false")
    if not receipt.get("effect_permitted") and not no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} missing despite effect_permitted=false")
    if receipt.get("security_review_required") and not review_exists:
        errors.append("security_review_ticket.json missing despite security_review_required=true")
    if receipt.get("quarantine_required") and not quarantine_exists:
        errors.append("quarantine_ticket.json missing despite quarantine_required=true")
    if not receipt.get("effect_permitted") and not (review_exists or quarantine_exists or suppression_exists):
        errors.append("non-permitted run has no review, quarantine, or suppression artifact")

    report = {
        "record_type": "verification_report",
        "case_id": run_dir.name,
        "verified": not errors,
        "tamper_detected": bool(errors),
        "errors": errors,
        "checked_files": checked,
    }
    if write_report:
        write_json(run_dir / "verification_report.json", report)
    return report


def run_case(input_path: Path, out_dir: Path, policy: dict[str, Any]) -> dict[str, Any]:
    req = read_json(input_path)
    case_id = req["case_id"]
    run_dir = out_dir / case_id
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)

    ev = instruction_evidence_bundle(req, policy)
    auth = authority_context(req, policy)
    boundary = prompt_boundary_analysis(req, policy)
    dec = evaluate(req, policy, ev, auth, boundary)
    receipt = build_decision_receipt(req, policy, ev, auth, boundary, dec)

    write_json(run_dir / "input_request.json", req)
    write_json(run_dir / "policy_snapshot.json", policy_snapshot(policy))
    write_json(run_dir / "instruction_evidence_bundle.json", ev)
    write_json(run_dir / "authority_context.json", auth)
    write_json(run_dir / "prompt_boundary_analysis.json", boundary)
    write_json(run_dir / "decision_receipt.json", receipt)

    if receipt["effect_permitted"]:
        write_json(run_dir / EFFECT_FILE, build_effect_record(req, receipt))
    else:
        (run_dir / NO_EFFECT_FILE).write_text(
            "No downstream boundary effect was created because evidence, authority, prompt boundary, or tool scope did not permit effect.\n",
            encoding="utf-8",
        )
        if receipt["quarantine_required"]:
            write_json(run_dir / "quarantine_ticket.json", build_quarantine_ticket(req, receipt, boundary))
            write_json(run_dir / "suppression_notice.json", build_suppression_notice(req, receipt))
        elif receipt["security_review_required"]:
            write_json(run_dir / "security_review_ticket.json", build_security_review_ticket(req, receipt))
        else:
            write_json(run_dir / "suppression_notice.json", build_suppression_notice(req, receipt))

    write_manifest(run_dir)
    report = verify_run(run_dir)
    return {
        "case_id": case_id,
        "lifecycle_status": receipt["lifecycle_status"],
        "reason_code": receipt["reason_code"],
        "effect_created": (run_dir / EFFECT_FILE).exists(),
        "verified": report["verified"],
    }


def run_suite(input_dir: Path, out_dir: Path, policy_path: Path) -> list[dict[str, Any]]:
    policy = load_policy(policy_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    return [run_case(path, out_dir, policy) for path in sorted(input_dir.glob("*.json"))]


def verify_suite(runs_dir: Path) -> list[dict[str, Any]]:
    if not runs_dir.exists():
        raise FileNotFoundError(f"Runs directory does not exist: {runs_dir}")
    reports = []
    for run_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        reports.append(verify_run(run_dir))
    return reports
