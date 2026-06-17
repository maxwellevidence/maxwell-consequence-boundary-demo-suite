from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

EXCLUDE_FROM_MANIFEST = {"manifest.json", "verification_report.json"}
EFFECT_FILE = "authorized_effect_record.json"
NO_EFFECT_FILE = "NO_AUTHORIZED_EFFECT_CREATED.txt"


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
    action = req.get("proposed_action") or {}
    llm = req.get("llm_output") or {}
    review = req.get("review") or {}
    parts = [
        action.get("description"),
        llm.get("recommendation"),
        llm.get("instruction_trace"),
        review.get("review_notes"),
    ]
    return " ".join(str(p or "") for p in parts).lower()


def prompt_injection_detected(req: dict[str, Any], policy: dict[str, Any]) -> bool:
    llm = req.get("llm_output") or {}
    if bool(llm.get("prompt_injection_detected")):
        return True
    blob = _text_blob(req)
    return any(str(indicator).lower() in blob for indicator in policy.get("prompt_injection_indicators") or [])


def required_refs_for_action(req: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    action = req.get("proposed_action") or {}
    refs = list(policy.get("base_required_evidence_refs") or [])
    if action.get("risk_level") in set(policy.get("review_required_risk_levels") or []):
        refs.extend(policy.get("high_risk_required_evidence_refs") or [])
    return sorted(set(refs))


def initial_evidence_bundle(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    evidence = req.get("evidence") or {}
    refs = list(evidence.get("refs") or [])
    required = required_refs_for_action(req, policy)
    missing = sorted(set(required) - set(refs))
    return {
        "record_type": "initial_evidence_bundle",
        "case_id": req["case_id"],
        "action_id": (req.get("proposed_action") or {}).get("action_id"),
        "evidence_refs": refs,
        "required_refs": required,
        "missing_refs": missing,
        "evidence_complete": not missing,
        "captured_at": evidence.get("captured_at"),
        "business_justification": evidence.get("business_justification"),
        "business_justification_present": bool(evidence.get("business_justification")),
        "prompt_injection_detected": prompt_injection_detected(req, policy),
        "instruction_trace_preserved": bool((req.get("llm_output") or {}).get("instruction_trace")),
    }


def initial_authority_context(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    actor = req.get("actor") or {}
    action = req.get("proposed_action") or {}
    role = actor.get("role")
    role_profile = dict((policy.get("proposer_roles") or {}).get(role) or {})
    allowed_scopes = set(role_profile.get("allowed_scopes") or [])
    allowed_effect_types = set(role_profile.get("allowed_effect_types") or [])
    allowed_targets = set(role_profile.get("allowed_target_systems") or [])
    return {
        "record_type": "initial_authority_context",
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
        "risk_level": action.get("risk_level"),
        "max_risk_without_review": role_profile.get("max_risk_without_review"),
        "risk_exceeds_no_review_threshold": risk_rank(policy, action.get("risk_level"))
        > risk_rank(policy, role_profile.get("max_risk_without_review")),
        "authority_present": bool(role_profile.get("can_propose_action")),
    }


def _decision(
    name: str,
    lifecycle: str,
    permitted: bool,
    review_required: bool,
    code: str,
    explanation: str,
    *,
    reviewable: bool = True,
) -> dict[str, Any]:
    return {
        "decision": name,
        "lifecycle_status": lifecycle,
        "effect_permitted": permitted,
        "review_required": review_required,
        "reviewable": reviewable,
        "reason_code": code,
        "explanation": explanation,
    }


def evaluate_initial(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    action = req.get("proposed_action") or {}
    ev = initial_evidence_bundle(req, policy)
    auth = initial_authority_context(req, policy)
    reason = policy["reason_codes"]

    if ev["prompt_injection_detected"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            reason["block_prompt_injection"],
            "Prompt-injected override language is preserved as evidence but cannot authorize effect.",
            reviewable=False,
        )
    if not auth["authority_present"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            reason["block_missing_authority"],
            "The proposer does not have authority to propose this action.",
            reviewable=False,
        )
    if not auth["effect_type_in_scope"] or not auth["scope_in_role_scope"] or not auth["target_in_role_scope"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            reason["block_scope_violation"],
            "The proposed action is outside the actor's approved scope, effect type, or target system.",
            reviewable=False,
        )
    if not ev["evidence_complete"]:
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            reason["review_missing_evidence"],
            "The action is reviewable, but required evidence is missing.",
        )
    if action.get("risk_level") in set(policy.get("review_required_risk_levels") or []) or auth[
        "risk_exceeds_no_review_threshold"
    ]:
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            reason["review_high_risk"],
            "The action is high risk and requires controlled human review.",
        )

    return _decision(
        "commit",
        "effect_committed",
        True,
        False,
        reason["effect_committed"],
        "Initial evidence and proposer authority are sufficient for downstream effect.",
    )


def build_initial_decision_receipt(
    req: dict[str, Any],
    policy: dict[str, Any],
    ev: dict[str, Any],
    auth: dict[str, Any],
    dec: dict[str, Any],
) -> dict[str, Any]:
    rec = {
        "record_type": "initial_decision_receipt",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "policy_hash": f"sha256:{policy['_policy_hash']}",
        "evaluated_at": policy.get("evaluation_time"),
        "evidence_bundle_hash": f"sha256:{sha_obj(ev)}",
        "authority_context_hash": f"sha256:{sha_obj(auth)}",
        **dec,
    }
    rec["initial_decision_receipt_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_review_event(req: dict[str, Any], initial_receipt: dict[str, Any]) -> dict[str, Any] | None:
    review = req.get("review") or {}
    if not review.get("submitted"):
        return None
    rec = {
        "record_type": "review_event",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "initial_decision_receipt_id": initial_receipt["initial_decision_receipt_id"],
        "submitted": True,
        "approval": review.get("approval"),
        "reviewer": review.get("reviewer") or {},
        "added_evidence_refs": list(review.get("added_evidence_refs") or []),
        "review_scope": review.get("review_scope"),
        "review_effect_type": review.get("review_effect_type"),
        "review_target_system": review.get("review_target_system"),
        "review_notes": review.get("review_notes"),
    }
    rec["review_event_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def review_authority_context(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any] | None:
    review = req.get("review") or {}
    if not review.get("submitted"):
        return None
    reviewer = review.get("reviewer") or {}
    action = req.get("proposed_action") or {}
    role = reviewer.get("role")
    role_profile = dict((policy.get("reviewer_roles") or {}).get(role) or {})
    allowed_scopes = set(role_profile.get("allowed_scopes") or [])
    allowed_effect_types = set(role_profile.get("allowed_effect_types") or [])
    allowed_targets = set(role_profile.get("allowed_target_systems") or [])
    return {
        "record_type": "review_authority_context",
        "case_id": req["case_id"],
        "reviewer_id": reviewer.get("reviewer_id"),
        "reviewer_role": role,
        "role_known": bool(role_profile),
        "can_review": bool(role_profile.get("can_review")),
        "same_as_proposer": reviewer.get("reviewer_id") == (req.get("actor") or {}).get("actor_id"),
        "max_review_risk": role_profile.get("max_review_risk"),
        "risk_within_review_authority": risk_rank(policy, action.get("risk_level"))
        <= risk_rank(policy, role_profile.get("max_review_risk")),
        "scope": action.get("scope"),
        "scope_in_review_scope": action.get("scope") in allowed_scopes,
        "effect_type": action.get("effect_type"),
        "effect_type_in_review_scope": action.get("effect_type") in allowed_effect_types,
        "target_system": action.get("target_system"),
        "target_in_review_scope": action.get("target_system") in allowed_targets,
        "authority_present": bool(role_profile.get("can_review")),
    }


def review_combined_evidence(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    evidence = req.get("evidence") or {}
    review = req.get("review") or {}
    initial_refs = list(evidence.get("refs") or [])
    added_refs = list(review.get("added_evidence_refs") or [])
    combined_refs = sorted(set(initial_refs + added_refs))
    required = required_refs_for_action(req, policy)
    missing = sorted(set(required) - set(combined_refs))
    return {
        "initial_refs": initial_refs,
        "added_refs": added_refs,
        "combined_refs": combined_refs,
        "required_refs": required,
        "missing_refs": missing,
        "evidence_complete_after_review": not missing,
    }


def evaluate_final(
    req: dict[str, Any],
    policy: dict[str, Any],
    initial_receipt: dict[str, Any],
    review_auth: dict[str, Any] | None,
) -> dict[str, Any]:
    reason = policy["reason_codes"]
    review = req.get("review") or {}
    action = req.get("proposed_action") or {}

    if initial_receipt["effect_permitted"]:
        return _decision(
            "commit",
            "effect_committed",
            True,
            False,
            reason["effect_committed"],
            "The original proposal was sufficiently evidenced and authorized.",
        )

    if not initial_receipt.get("reviewable"):
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            initial_receipt["reason_code"],
            "The original proposal is non-reviewable under this public-preview policy.",
            reviewable=False,
        )

    if not initial_receipt["review_required"]:
        return _decision(
            "suppress",
            "effect_suppressed",
            False,
            False,
            initial_receipt["reason_code"],
            "The original proposal did not create a reviewable path to effect.",
            reviewable=False,
        )

    if not review.get("submitted"):
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            initial_receipt["reason_code"],
            "The action remains in review because no reviewer decision was submitted.",
        )

    if review.get("review_scope") != action.get("scope") or review.get("review_effect_type") != action.get(
        "effect_type"
    ) or review.get("review_target_system") != action.get("target_system"):
        return _decision(
            "suppress",
            "review_rejected_effect_suppressed",
            False,
            False,
            reason["block_scope_expansion"],
            "Review attempted to change the scope, effect type, or target system of the original proposal.",
            reviewable=False,
        )

    if not review_auth or not review_auth["authority_present"] or not review_auth["role_known"]:
        return _decision(
            "suppress",
            "review_rejected_effect_suppressed",
            False,
            False,
            reason["reviewer_lacks_authority"],
            "The submitted reviewer does not have review authority.",
        )
    if review_auth["same_as_proposer"]:
        return _decision(
            "suppress",
            "review_rejected_effect_suppressed",
            False,
            False,
            reason["reviewer_lacks_authority"],
            "Self-review is not sufficient authority for downstream effect.",
        )
    if not review_auth["risk_within_review_authority"] or not review_auth["scope_in_review_scope"]:
        return _decision(
            "suppress",
            "review_rejected_effect_suppressed",
            False,
            False,
            reason["reviewer_lacks_authority"],
            "The reviewer lacks authority for this risk level or action scope.",
        )
    if not review_auth["effect_type_in_review_scope"] or not review_auth["target_in_review_scope"]:
        return _decision(
            "suppress",
            "review_rejected_effect_suppressed",
            False,
            False,
            reason["reviewer_lacks_authority"],
            "The reviewer lacks authority for this effect type or target system.",
        )
    if review.get("approval") != "approve":
        return _decision(
            "suppress",
            "review_rejected_effect_suppressed",
            False,
            False,
            reason["review_failed"],
            "The reviewer did not approve the action.",
        )

    combined = review_combined_evidence(req, policy)
    if not combined["evidence_complete_after_review"]:
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            reason["review_missing_evidence_after_review"],
            "Review was submitted, but required evidence remains incomplete.",
        )

    return _decision(
        "commit_after_review",
        "review_approved_effect_committed",
        True,
        False,
        reason["review_approved_effect_committed"],
        "Controlled review supplied sufficient evidence and reviewer authority for effect.",
    )


def build_final_decision_receipt(
    req: dict[str, Any],
    policy: dict[str, Any],
    initial_receipt: dict[str, Any],
    review_event: dict[str, Any] | None,
    review_auth: dict[str, Any] | None,
    final_decision: dict[str, Any],
) -> dict[str, Any]:
    rec = {
        "record_type": "decision_receipt",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "policy_hash": f"sha256:{policy['_policy_hash']}",
        "evaluated_at": policy.get("evaluation_time"),
        "initial_decision_receipt_id": initial_receipt["initial_decision_receipt_id"],
        "review_event_id": review_event.get("review_event_id") if review_event else None,
        "review_authority_context_hash": f"sha256:{sha_obj(review_auth)}" if review_auth else None,
        **final_decision,
    }
    rec["decision_receipt_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_effect_record(req: dict[str, Any], receipt: dict[str, Any], review_auth: dict[str, Any] | None) -> dict[str, Any]:
    action = req["proposed_action"]
    reviewer = (req.get("review") or {}).get("reviewer") or {}
    rec = {
        "record_type": "authorized_effect_record",
        "case_id": req["case_id"],
        "action_id": action.get("action_id"),
        "effect_type": action.get("effect_type"),
        "scope": action.get("scope"),
        "target_system": action.get("target_system"),
        "effect_payload": action.get("requested_change"),
        "effect_basis": receipt["decision_receipt_id"],
        "effect_committed": True,
        "reviewer_id": reviewer.get("reviewer_id") if review_auth else None,
        "reviewer_role": review_auth.get("reviewer_role") if review_auth else None,
        "note": "This synthetic demo records an authorized effect; it does not call downstream systems.",
    }
    rec["effect_record_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_review_ticket(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "review_ticket",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "review_queue": "controlled_human_review_queue",
        "reason_code": receipt["reason_code"],
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["review_ticket_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_review_rejection_notice(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "review_rejection_notice",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"].get("action_id"),
        "reason_code": receipt["reason_code"],
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["review_rejection_notice_id"] = f"sha256:{sha_obj(rec)}"
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
    review_ticket_exists = (run_dir / "review_ticket.json").exists()
    review_rejection_exists = (run_dir / "review_rejection_notice.json").exists()
    suppression_exists = (run_dir / "suppression_notice.json").exists()

    if receipt.get("effect_permitted") and not effect_exists:
        errors.append(f"{EFFECT_FILE} missing despite effect_permitted=true")
    if receipt.get("effect_permitted") and no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} exists despite effect_permitted=true")
    if not receipt.get("effect_permitted") and effect_exists:
        errors.append(f"{EFFECT_FILE} exists despite effect_permitted=false")
    if not receipt.get("effect_permitted") and not no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} missing despite effect_permitted=false")
    if receipt.get("review_required") and not review_ticket_exists:
        errors.append("review_ticket.json missing despite review_required=true")
    if receipt.get("lifecycle_status") == "review_rejected_effect_suppressed" and not review_rejection_exists:
        errors.append("review_rejection_notice.json missing for rejected review")
    if receipt.get("lifecycle_status") == "effect_suppressed" and not suppression_exists:
        errors.append("suppression_notice.json missing for suppressed effect")

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

    ev = initial_evidence_bundle(req, policy)
    auth = initial_authority_context(req, policy)
    initial_dec = evaluate_initial(req, policy)
    initial_receipt = build_initial_decision_receipt(req, policy, ev, auth, initial_dec)
    review_event = build_review_event(req, initial_receipt)
    review_auth = review_authority_context(req, policy)
    final_dec = evaluate_final(req, policy, initial_receipt, review_auth)
    final_receipt = build_final_decision_receipt(
        req, policy, initial_receipt, review_event, review_auth, final_dec
    )

    write_json(run_dir / "input_request.json", req)
    write_json(run_dir / "policy_snapshot.json", policy_snapshot(policy))
    write_json(run_dir / "initial_evidence_bundle.json", ev)
    write_json(run_dir / "initial_authority_context.json", auth)
    write_json(run_dir / "initial_decision_receipt.json", initial_receipt)
    if review_event:
        write_json(run_dir / "review_event.json", review_event)
    if review_auth:
        write_json(run_dir / "review_authority_context.json", review_auth)
    write_json(run_dir / "decision_receipt.json", final_receipt)

    if final_receipt["effect_permitted"]:
        write_json(run_dir / EFFECT_FILE, build_effect_record(req, final_receipt, review_auth))
    else:
        (run_dir / NO_EFFECT_FILE).write_text(
            "No authorized downstream effect was created because review evidence and authority did not permit effect.\n",
            encoding="utf-8",
        )
        if final_receipt["review_required"]:
            write_json(run_dir / "review_ticket.json", build_review_ticket(req, final_receipt))
        elif final_receipt["lifecycle_status"] == "review_rejected_effect_suppressed":
            write_json(run_dir / "review_rejection_notice.json", build_review_rejection_notice(req, final_receipt))
        else:
            write_json(run_dir / "suppression_notice.json", build_suppression_notice(req, final_receipt))

    write_manifest(run_dir)
    report = verify_run(run_dir)
    return {
        "case_id": case_id,
        "lifecycle_status": final_receipt["lifecycle_status"],
        "reason_code": final_receipt["reason_code"],
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
