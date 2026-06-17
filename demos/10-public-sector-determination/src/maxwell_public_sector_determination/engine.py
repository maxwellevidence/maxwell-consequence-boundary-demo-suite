from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

EXCLUDE_FROM_MANIFEST = {"manifest.json", "verification_report.json"}
EFFECT_FILE = "determination_effect_record.json"
NO_EFFECT_FILE = "NO_DETERMINATION_EFFECT_CREATED.txt"


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
    ai = req.get("ai_recommendation") or {}
    external = req.get("external_instruction") or {}
    proposed = req.get("proposed_determination") or {}
    parts = [
        external.get("text"),
        ai.get("recommendation"),
        ai.get("rationale"),
        ai.get("instruction_trace"),
        proposed.get("description"),
    ]
    return " ".join(str(p or "") for p in parts).lower()


def due_process_analysis(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    proposed = req.get("proposed_determination") or {}
    evidence = req.get("evidence") or {}
    review = req.get("review") or {}
    ai = req.get("ai_recommendation") or {}
    blob = _text_blob(req)
    indicators = [
        str(indicator)
        for indicator in policy.get("unsafe_instruction_indicators") or []
        if str(indicator).lower() in blob
    ]
    adverse_types = set(policy.get("adverse_determination_types") or [])
    adverse = bool(proposed.get("adverse") or proposed.get("determination_type") in adverse_types)
    appeal_notice = bool(evidence.get("appeal_rights_notice_attached"))
    written_notice = "notice_template_attached" in set(evidence.get("refs") or [])
    human_review_complete = bool(review.get("review_complete"))
    ai_claims_final_authority = bool(ai.get("claims_final_authority"))
    automated_final_action_requested = bool(
        proposed.get("requested_final_action") == "auto_bind" or ai.get("recommendation") == "auto_finalize"
    )
    return {
        "record_type": "due_process_analysis",
        "case_id": req["case_id"],
        "adverse_determination": adverse,
        "appeal_rights_notice_attached": appeal_notice,
        "written_notice_attached": written_notice,
        "human_review_complete": human_review_complete,
        "ai_claims_final_authority": ai_claims_final_authority,
        "automated_final_action_requested": automated_final_action_requested,
        "unsafe_instruction_indicators": sorted(set(indicators)),
        "unsafe_instruction_detected": bool(indicators),
        "ai_output_treated_as_authority": False,
    }


def required_refs_for_case(req: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    proposed = req.get("proposed_determination") or {}
    program = proposed.get("program")
    refs = list(policy.get("base_required_evidence_refs") or [])
    refs.extend((policy.get("program_required_evidence_refs") or {}).get(program) or [])
    if proposed.get("risk_level") in set(policy.get("high_risk_levels") or []):
        refs.extend(policy.get("high_risk_required_evidence_refs") or [])
    if proposed.get("adverse") or proposed.get("determination_type") in set(policy.get("adverse_determination_types") or []):
        refs.extend(policy.get("adverse_required_evidence_refs") or [])
    return sorted(set(refs))


def determination_evidence_bundle(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    evidence = req.get("evidence") or {}
    proposed = req.get("proposed_determination") or {}
    refs = list(evidence.get("refs") or [])
    required = required_refs_for_case(req, policy)
    missing = sorted(set(required) - set(refs))
    return {
        "record_type": "determination_evidence_bundle",
        "case_id": req["case_id"],
        "case_record_id": (req.get("case_record") or {}).get("case_record_id"),
        "determination_id": proposed.get("determination_id"),
        "program": proposed.get("program"),
        "evidence_refs": refs,
        "required_refs": required,
        "missing_refs": missing,
        "evidence_complete": not missing,
        "case_record_consistent": bool(evidence.get("case_record_consistent")),
        "appeal_rights_notice_attached": bool(evidence.get("appeal_rights_notice_attached")),
        "captured_at": evidence.get("captured_at"),
        "synthetic_record": True,
    }


def review_authority_context(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    review = req.get("review") or {}
    reviewer_role = review.get("reviewer_role")
    profile = dict((policy.get("review_roles") or {}).get(reviewer_role) or {})
    proposed = req.get("proposed_determination") or {}
    allowed_programs = set(profile.get("allowed_programs") or [])
    allowed_determinations = set(profile.get("allowed_determination_types") or [])
    return {
        "record_type": "review_authority_context",
        "case_id": req["case_id"],
        "review_submitted": bool(review),
        "review_id": review.get("review_id"),
        "reviewer_id": review.get("reviewer_id"),
        "reviewer_role": reviewer_role,
        "reviewer_role_known": bool(profile),
        "review_complete": bool(review.get("review_complete")),
        "review_disposition": review.get("review_disposition"),
        "reviewer_can_authorize_adverse_effect": bool(profile.get("can_authorize_adverse_effect")),
        "program_in_reviewer_scope": proposed.get("program") in allowed_programs if profile else False,
        "determination_type_in_reviewer_scope": proposed.get("determination_type") in allowed_determinations
        if profile
        else False,
        "review_authority_present": bool(
            profile
            and review.get("review_complete")
            and proposed.get("program") in allowed_programs
            and proposed.get("determination_type") in allowed_determinations
        ),
    }


def authority_context(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    actor = req.get("actor") or {}
    proposed = req.get("proposed_determination") or {}
    role = actor.get("role")
    profile = dict((policy.get("roles") or {}).get(role) or {})
    allowed_programs = set(profile.get("allowed_programs") or [])
    allowed_jurisdictions = set(profile.get("allowed_jurisdictions") or [])
    allowed_determinations = set(profile.get("allowed_determination_types") or [])
    return {
        "record_type": "authority_context",
        "case_id": req["case_id"],
        "actor_id": actor.get("actor_id"),
        "actor_role": role,
        "role_known": bool(profile),
        "can_propose_determination": bool(profile.get("can_propose_determination")),
        "can_bind_non_adverse_effect": bool(profile.get("can_bind_non_adverse_effect")),
        "can_bind_adverse_effect": bool(profile.get("can_bind_adverse_effect")),
        "program": proposed.get("program"),
        "program_in_role_scope": proposed.get("program") in allowed_programs,
        "jurisdiction": proposed.get("jurisdiction"),
        "jurisdiction_in_role_scope": proposed.get("jurisdiction") in allowed_jurisdictions,
        "determination_type": proposed.get("determination_type"),
        "determination_type_in_role_scope": proposed.get("determination_type") in allowed_determinations,
        "risk_level": proposed.get("risk_level"),
        "max_risk_without_review": profile.get("max_risk_without_review"),
        "risk_exceeds_no_review_threshold": risk_rank(policy, proposed.get("risk_level"))
        > risk_rank(policy, profile.get("max_risk_without_review")),
        "authority_present": bool(profile.get("can_propose_determination")),
    }


def _decision(
    name: str,
    lifecycle: str,
    permitted: bool,
    review_required: bool,
    due_process_required: bool,
    code: str,
    explanation: str,
) -> dict[str, Any]:
    return {
        "decision": name,
        "lifecycle_status": lifecycle,
        "effect_permitted": permitted,
        "case_review_required": review_required,
        "due_process_review_required": due_process_required,
        "reason_code": code,
        "explanation": explanation,
    }


def evaluate(
    req: dict[str, Any],
    policy: dict[str, Any],
    ev: dict[str, Any],
    auth: dict[str, Any],
    review_auth: dict[str, Any],
    due: dict[str, Any],
) -> dict[str, Any]:
    reason = policy["reason_codes"]
    proposed = req.get("proposed_determination") or {}
    adverse = bool(due["adverse_determination"])

    if due["ai_claims_final_authority"] or due["automated_final_action_requested"]:
        return _decision(
            "suppress",
            "determination_effect_suppressed",
            False,
            False,
            False,
            reason["unauthorized_automated_adverse_determination"],
            "AI output may recommend a determination, but it cannot bind a public-sector determination.",
        )
    if due["unsafe_instruction_detected"]:
        return _decision(
            "suppress",
            "determination_effect_suppressed",
            False,
            False,
            False,
            reason["unsafe_instruction_preserved"],
            "Unsafe instruction text was preserved as evidence and was not treated as authority.",
        )
    if not auth["authority_present"] or not auth["role_known"]:
        return _decision(
            "suppress",
            "determination_effect_suppressed",
            False,
            False,
            False,
            reason["missing_case_authority"],
            "The actor lacks recognized authority to propose this determination.",
        )
    if not auth["program_in_role_scope"] or not auth["jurisdiction_in_role_scope"]:
        return _decision(
            "suppress",
            "determination_effect_suppressed",
            False,
            False,
            False,
            reason["program_or_jurisdiction_scope_violation"],
            "The program or jurisdiction is outside the actor's authority scope.",
        )
    if not auth["determination_type_in_role_scope"]:
        return _decision(
            "suppress",
            "determination_effect_suppressed",
            False,
            False,
            False,
            reason["determination_type_scope_violation"],
            "The determination type is outside the actor's authority scope.",
        )
    if not ev["case_record_consistent"]:
        return _decision(
            "review",
            "case_review_routed",
            False,
            True,
            False,
            reason["case_record_inconsistent_requires_review"],
            "The case record is inconsistent; no binding effect is created until review.",
        )
    if not ev["evidence_complete"]:
        return _decision(
            "review",
            "case_review_routed",
            False,
            True,
            False,
            reason["required_eligibility_evidence_missing"],
            "Required eligibility or notice evidence is missing; no determination effect is created.",
        )

    adverse_needs_review = bool(adverse or auth["risk_exceeds_no_review_threshold"])
    if adverse_needs_review:
        if not due["appeal_rights_notice_attached"] or not due["written_notice_attached"]:
            return _decision(
                "due_process_review",
                "due_process_review_routed",
                False,
                True,
                True,
                reason["notice_and_appeal_rights_missing"],
                "Adverse or high-risk determinations require notice and appeal-rights evidence.",
            )
        if not review_auth["review_authority_present"]:
            return _decision(
                "due_process_review",
                "due_process_review_routed",
                False,
                True,
                True,
                reason["due_process_review_required"],
                "Adverse or high-risk determinations require authorized human review before effect.",
            )
        if review_auth["review_disposition"] not in {"approve_effect", "approve_determination"}:
            return _decision(
                "due_process_review",
                "due_process_review_routed",
                False,
                True,
                True,
                reason["due_process_review_required"],
                "The review event does not authorize the proposed determination effect.",
            )

    if adverse and not auth["can_bind_adverse_effect"] and not review_auth["review_authority_present"]:
        return _decision(
            "due_process_review",
            "due_process_review_routed",
            False,
            True,
            True,
            reason["due_process_review_required"],
            "Adverse effect requires reviewer authority in this public preview.",
        )
    if not adverse and not auth["can_bind_non_adverse_effect"]:
        return _decision(
            "review",
            "case_review_routed",
            False,
            True,
            False,
            reason["due_process_review_required"],
            "The actor may propose but may not bind this determination without review.",
        )

    explanation = "Eligibility evidence, actor authority, and public-review context are sufficient."
    if adverse:
        explanation = "Adverse determination effect is permitted only after notice, appeal-rights evidence, and authorized human review."
    return _decision(
        "commit",
        "determination_effect_committed",
        True,
        False,
        False,
        reason["determination_effect_committed"],
        explanation,
    )


def build_decision_receipt(
    req: dict[str, Any],
    policy: dict[str, Any],
    ev: dict[str, Any],
    auth: dict[str, Any],
    review_auth: dict[str, Any],
    due: dict[str, Any],
    dec: dict[str, Any],
) -> dict[str, Any]:
    rec = {
        "record_type": "decision_receipt",
        "case_id": req["case_id"],
        "case_record_id": (req.get("case_record") or {}).get("case_record_id"),
        "determination_id": req["proposed_determination"].get("determination_id"),
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "policy_hash": f"sha256:{policy['_policy_hash']}",
        "evaluated_at": policy.get("evaluation_time"),
        "determination_evidence_bundle_hash": f"sha256:{sha_obj(ev)}",
        "authority_context_hash": f"sha256:{sha_obj(auth)}",
        "review_authority_context_hash": f"sha256:{sha_obj(review_auth)}",
        "due_process_analysis_hash": f"sha256:{sha_obj(due)}",
        **dec,
    }
    rec["decision_receipt_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_effect_record(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    proposed = req["proposed_determination"]
    case_record = req.get("case_record") or {}
    rec = {
        "record_type": "determination_effect_record",
        "case_id": req["case_id"],
        "case_record_id": case_record.get("case_record_id"),
        "determination_id": proposed.get("determination_id"),
        "program": proposed.get("program"),
        "jurisdiction": proposed.get("jurisdiction"),
        "determination_type": proposed.get("determination_type"),
        "adverse": bool(proposed.get("adverse")),
        "determination_effect": proposed.get("determination_effect"),
        "effect_basis": receipt["decision_receipt_id"],
        "binding_effect_committed": True,
        "note": "This synthetic demo records a determination effect; it does not connect to public systems.",
    }
    rec["determination_effect_record_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_case_review_ticket(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    proposed = req.get("proposed_determination") or {}
    rec = {
        "record_type": "case_review_ticket",
        "case_id": req["case_id"],
        "case_record_id": (req.get("case_record") or {}).get("case_record_id"),
        "determination_id": proposed.get("determination_id"),
        "review_queue": "public_sector_case_review",
        "reason_code": receipt["reason_code"],
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["case_review_ticket_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_due_process_review_ticket(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    proposed = req.get("proposed_determination") or {}
    rec = {
        "record_type": "due_process_review_ticket",
        "case_id": req["case_id"],
        "case_record_id": (req.get("case_record") or {}).get("case_record_id"),
        "determination_id": proposed.get("determination_id"),
        "review_queue": "public_sector_due_process_review",
        "reason_code": receipt["reason_code"],
        "notice_and_appeal_review_required": True,
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["due_process_review_ticket_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_suppression_notice(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "suppression_notice",
        "case_id": req["case_id"],
        "case_record_id": (req.get("case_record") or {}).get("case_record_id"),
        "determination_id": req["proposed_determination"].get("determination_id"),
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
    case_review_exists = (run_dir / "case_review_ticket.json").exists()
    due_process_exists = (run_dir / "due_process_review_ticket.json").exists()
    suppression_exists = (run_dir / "suppression_notice.json").exists()

    if receipt.get("effect_permitted") and not effect_exists:
        errors.append(f"{EFFECT_FILE} missing despite effect_permitted=true")
    if receipt.get("effect_permitted") and no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} exists despite effect_permitted=true")
    if not receipt.get("effect_permitted") and effect_exists:
        errors.append(f"{EFFECT_FILE} exists despite effect_permitted=false")
    if not receipt.get("effect_permitted") and not no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} missing despite effect_permitted=false")
    if receipt.get("case_review_required") and not (case_review_exists or due_process_exists):
        errors.append("review ticket missing despite case_review_required=true")
    if receipt.get("due_process_review_required") and not due_process_exists:
        errors.append("due_process_review_ticket.json missing despite due_process_review_required=true")
    if not receipt.get("effect_permitted") and not (case_review_exists or due_process_exists or suppression_exists):
        errors.append("non-permitted run has no review or suppression artifact")

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

    ev = determination_evidence_bundle(req, policy)
    auth = authority_context(req, policy)
    review_auth = review_authority_context(req, policy)
    due = due_process_analysis(req, policy)
    dec = evaluate(req, policy, ev, auth, review_auth, due)
    receipt = build_decision_receipt(req, policy, ev, auth, review_auth, due, dec)

    write_json(run_dir / "input_request.json", req)
    write_json(run_dir / "policy_snapshot.json", policy_snapshot(policy))
    write_json(run_dir / "determination_evidence_bundle.json", ev)
    write_json(run_dir / "authority_context.json", auth)
    write_json(run_dir / "review_authority_context.json", review_auth)
    write_json(run_dir / "due_process_analysis.json", due)
    write_json(run_dir / "decision_receipt.json", receipt)

    if receipt["effect_permitted"]:
        write_json(run_dir / EFFECT_FILE, build_effect_record(req, receipt))
    else:
        (run_dir / NO_EFFECT_FILE).write_text(
            "No public-sector determination effect was created because evidence, authority, or due-process context did not permit binding effect.\n",
            encoding="utf-8",
        )
        if receipt["due_process_review_required"]:
            write_json(run_dir / "due_process_review_ticket.json", build_due_process_review_ticket(req, receipt))
        elif receipt["case_review_required"]:
            write_json(run_dir / "case_review_ticket.json", build_case_review_ticket(req, receipt))
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
