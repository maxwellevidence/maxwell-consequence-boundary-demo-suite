from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

EXCLUDE_FROM_MANIFEST = {"manifest.json", "verification_report.json"}


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


def risk_value(policy: dict[str, Any], value: str | None) -> int:
    return int((policy.get("risk_order") or {}).get(str(value or "").lower(), 999))


def role_rank(policy: dict[str, Any], role: str | None) -> int:
    return int((policy.get("role_rank") or {}).get(str(role or ""), -1))


def evidence_bundle(req: dict[str, Any], policy: dict[str, Any], record_type: str) -> dict[str, Any]:
    refs = list((req.get("evidence") or {}).get("refs") or [])
    required = list(policy.get("required_evidence_refs") or [])
    missing = sorted(set(required) - set(refs))
    return {
        "record_type": record_type,
        "case_id": req["case_id"],
        "evidence_refs": refs,
        "required_refs_under_policy": required,
        "missing_refs_under_policy": missing,
        "complete_under_policy": not missing,
        "captured_at": (req.get("evidence") or {}).get("captured_at"),
        "policy_version": policy["policy_version"],
    }


def authority_context(req: dict[str, Any], policy: dict[str, Any], record_type: str) -> dict[str, Any]:
    auth = req.get("authority") or {}
    action = req["proposed_action"]
    role = auth.get("approver_role")
    profile = dict((policy.get("authority_roles") or {}).get(role) or {})
    allowed_systems = list(profile.get("authorized_systems") or [])
    allowed_effects = list(profile.get("allowed_effect_types") or [])
    effect = action.get("requested_effect")
    minimum_role = (policy.get("minimum_role_by_effect") or {}).get(effect)
    permitted_exact_roles = list((policy.get("permitted_approver_roles_by_effect") or {}).get(effect) or [])
    dual_control_required = effect in set(policy.get("dual_control_required_effects") or [])
    return {
        "record_type": record_type,
        "case_id": req["case_id"],
        "policy_version": policy["policy_version"],
        "actor_id": auth.get("actor_id"),
        "approver_id": auth.get("approver_id"),
        "approver_role": role,
        "role_known": bool(profile),
        "role_profile": profile,
        "can_commit_effect": bool(profile.get("can_commit_effect")),
        "requested_effect": effect,
        "allowed_effect_types_for_role": allowed_effects,
        "effect_in_role_scope": effect in set(allowed_effects),
        "target_system": action.get("target_system"),
        "authorized_systems_for_role": allowed_systems,
        "target_in_scope": action.get("target_system") in set(allowed_systems),
        "risk_level": action.get("risk_level"),
        "max_risk_for_role": profile.get("max_risk"),
        "risk_within_role_limit": risk_value(policy, action.get("risk_level")) <= risk_value(policy, profile.get("max_risk")),
        "minimum_role_for_effect": minimum_role,
        "role_meets_minimum": role_rank(policy, role) >= role_rank(policy, minimum_role),
        "permitted_exact_roles_for_effect": permitted_exact_roles,
        "exact_role_requirement_satisfied": not permitted_exact_roles or role in set(permitted_exact_roles),
        "dual_control_required": dual_control_required,
        "dual_control_present": bool(auth.get("dual_control")),
        "second_approver_role": auth.get("second_approver_role"),
        "authority_present": bool(auth.get("approver_id") and profile.get("can_commit_effect")),
    }


def _decision(
    name: str,
    lifecycle: str,
    permitted: bool,
    review: bool,
    code: str,
    explanation: str,
) -> dict[str, Any]:
    return {
        "decision": name,
        "lifecycle_status": lifecycle,
        "effect_permitted": permitted,
        "review_required": review,
        "reason_code": code,
        "explanation": explanation,
    }


def evaluate(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    action = req["proposed_action"]
    effect = action.get("requested_effect")
    ev = evidence_bundle(req, policy, "evidence_evaluation")
    auth = authority_context(req, policy, "authority_evaluation")
    reason = policy["reason_codes"]

    if effect not in set(policy.get("allowed_effect_types") or []):
        return _decision("block", "effect_suppressed", False, False, reason["block_forbidden_effect"], "Requested effect type is not allowed by the evaluated policy.")
    if not ev["complete_under_policy"]:
        return _decision("review", "review_routed", False, True, reason["review_missing_evidence"], "Required evidence is missing under the evaluated policy.")
    if not auth["authority_present"]:
        return _decision("block", "effect_suppressed", False, False, reason["block_missing_authority"], "No valid authority context supports downstream effect.")
    if not auth["target_in_scope"]:
        return _decision("block", "effect_suppressed", False, False, reason["block_scope_violation"], "Target system is outside the approver's policy scope.")
    if not auth["effect_in_role_scope"]:
        return _decision("block", "effect_suppressed", False, False, reason["block_effect_not_in_role_scope"], "Approver role is not permitted to commit this effect type.")
    if not auth["role_meets_minimum"]:
        return _decision("review", "review_routed", False, True, reason["review_role_insufficient"], "Approver role does not meet the minimum role required for the effect.")
    if not auth["exact_role_requirement_satisfied"]:
        return _decision("review", "review_routed", False, True, reason["review_approver_role_required"], "A policy-specific approver role is required for this effect.")
    if auth["dual_control_required"] and not auth["dual_control_present"]:
        return _decision("review", "review_routed", False, True, reason["review_dual_control_required"], "Dual control is required under the evaluated policy.")
    if not auth["risk_within_role_limit"]:
        return _decision("review", "review_routed", False, True, reason["review_role_risk_limit"], "Requested risk exceeds the role's policy limit.")
    if risk_value(policy, action.get("risk_level")) >= risk_value(policy, policy.get("review_required_risk_at_or_above")):
        return _decision("review", "review_routed", False, True, reason["review_risk_threshold"], "Risk level meets the policy review threshold.")
    return _decision("allow", "effect_committed", True, False, reason["allow"], "Evidence, authority, scope, and risk requirements are satisfied under the evaluated policy.")


def build_decision_receipt(
    req: dict[str, Any],
    policy: dict[str, Any],
    ev: dict[str, Any],
    auth: dict[str, Any],
    dec: dict[str, Any],
) -> dict[str, Any]:
    rec = {
        "record_type": "decision_receipt",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"]["action_id"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "policy_hash": f"sha256:{policy['_policy_hash']}",
        "evaluated_at": policy.get("evaluation_time"),
        "evidence_bundle_hash": f"sha256:{sha_obj(ev)}",
        "authority_context_hash": f"sha256:{sha_obj(auth)}",
        **dec,
    }
    rec["decision_receipt_id"] = f"sha256:{sha_obj(rec)}"
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
    receipt = read_json(run_dir / "decision_receipt.json") if (run_dir / "decision_receipt.json").exists() else {}
    effect_exists = (run_dir / "effect_record.json").exists()
    if receipt.get("effect_permitted") and not effect_exists:
        errors.append("effect_record.json missing despite effect_permitted=true")
    if not receipt.get("effect_permitted") and effect_exists:
        errors.append("effect_record.json exists despite effect_permitted=false")
    if not receipt.get("effect_permitted") and not (run_dir / "NO_EFFECT_CREATED.txt").exists():
        errors.append("NO_EFFECT_CREATED.txt missing despite effect_permitted=false")
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
    run_dir = out_dir / req["case_id"]
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    ev = evidence_bundle(req, policy, "original_evidence_bundle")
    auth = authority_context(req, policy, "original_authority_context")
    dec = evaluate(req, policy)
    receipt = build_decision_receipt(req, policy, ev, auth, dec)

    write_json(run_dir / "input_request.json", req)
    write_json(run_dir / "original_evidence_bundle.json", ev)
    write_json(run_dir / "original_authority_context.json", auth)
    write_json(run_dir / "original_policy_snapshot.json", policy_snapshot(policy))
    write_json(run_dir / "decision_receipt.json", receipt)

    if dec["effect_permitted"]:
        write_json(
            run_dir / "effect_record.json",
            {
                "record_type": "effect_record",
                "case_id": req["case_id"],
                "action_id": req["proposed_action"]["action_id"],
                "effect_type": req["proposed_action"]["requested_effect"],
                "target_system": req["proposed_action"]["target_system"],
                "created_under_policy_version": policy["policy_version"],
                "decision_receipt_hash": f"sha256:{sha_obj(receipt)}",
                "synthetic_no_real_execution": True,
            },
        )
    else:
        (run_dir / "NO_EFFECT_CREATED.txt").write_text("No downstream effect was created under the original policy.\n", encoding="utf-8")
        if dec["review_required"]:
            write_json(run_dir / "review_ticket.json", {"record_type": "review_ticket", "case_id": req["case_id"], "reason_code": dec["reason_code"], "review_queue": "policy_replay_governance_review", "effect_created": False})
        else:
            write_json(run_dir / "suppression_notice.json", {"record_type": "suppression_notice", "case_id": req["case_id"], "reason_code": dec["reason_code"], "effect_created": False})

    write_json(
        run_dir / "timeline_event.json",
        {
            "record_type": "timeline_event",
            "case_id": req["case_id"],
            "event_sequence": [
                "PROPOSED",
                "ORIGINAL_EVIDENCE_CAPTURED",
                "ORIGINAL_AUTHORITY_EVALUATED",
                "POLICY_AT_TIME_APPLIED",
                dec["lifecycle_status"].upper(),
                "ORIGINAL_RECORD_SEALED_FOR_REPLAY",
            ],
            "effect_created": dec["effect_permitted"],
        },
    )
    write_manifest(run_dir)
    verification = verify_run(run_dir, write_report=True)
    return {"case_id": req["case_id"], "lifecycle_status": dec["lifecycle_status"], "effect_created": dec["effect_permitted"], "verified": verification["verified"]}


def run_suite(input_dir: Path, out_dir: Path, policy_path: Path) -> list[dict[str, Any]]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    policy = load_policy(policy_path)
    results = [run_case(p, out_dir, policy) for p in sorted(input_dir.glob("*.json"))]
    write_json(out_dir / "_suite_summary.json", {"record_type": "suite_summary", "runs": results})
    return results


def verify_suite(runs_dir: Path) -> list[dict[str, Any]]:
    return [verify_run(d, True) for d in sorted(p for p in runs_dir.iterdir() if p.is_dir())]


def classify_drift(original: dict[str, Any], replay: dict[str, Any]) -> str:
    orig_permitted = bool(original.get("effect_permitted"))
    replay_permitted = bool(replay.get("effect_permitted"))
    orig_decision = original.get("decision")
    replay_decision = replay.get("decision")
    if orig_decision == replay_decision and orig_permitted == replay_permitted:
        return "NO_OUTCOME_CHANGE"
    if orig_permitted and replay_decision == "review":
        return "PREVIOUSLY_ALLOWED_NOW_REVIEW"
    if orig_permitted and replay_decision == "block":
        return "PREVIOUSLY_ALLOWED_NOW_BLOCK"
    if not orig_permitted and replay_permitted:
        return "PREVIOUSLY_SUPPRESSED_NOW_ALLOWED"
    if not orig_permitted and not replay_permitted:
        return "PREVIOUSLY_SUPPRESSED_STILL_SUPPRESSED_WITH_CHANGED_REASON"
    return "OUTCOME_CHANGED"


def replay_case(run_dir: Path, target_policy: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    req = read_json(run_dir / "input_request.json")
    original_receipt = read_json(run_dir / "decision_receipt.json")
    original_policy = read_json(run_dir / "original_policy_snapshot.json")
    original_verified = verify_run(run_dir, write_report=False)
    effect_before = (run_dir / "effect_record.json").exists()
    effect_hash_before = sha_file(run_dir / "effect_record.json") if effect_before else None

    replay_ev = evidence_bundle(req, target_policy, "replay_evidence_bundle")
    replay_auth = authority_context(req, target_policy, "replay_authority_context")
    replay_dec = evaluate(req, target_policy)
    replay_receipt = build_decision_receipt(req, target_policy, replay_ev, replay_auth, replay_dec)

    effect_after = (run_dir / "effect_record.json").exists()
    effect_hash_after = sha_file(run_dir / "effect_record.json") if effect_after else None
    effect_record_mutated = (effect_before != effect_after) or (effect_hash_before != effect_hash_after)
    drift_class = classify_drift(original_receipt, replay_dec)

    report = {
        "record_type": "policy_replay_report",
        "case_id": req["case_id"],
        "original_integrity": {
            "verified_before_replay": original_verified["verified"],
            "tamper_detected": original_verified["tamper_detected"],
            "errors": original_verified["errors"],
        },
        "original_policy": {
            "policy_id": original_policy["policy_id"],
            "policy_version": original_policy["policy_version"],
            "policy_hash": original_policy["policy_hash"],
        },
        "target_policy": {
            "policy_id": target_policy["policy_id"],
            "policy_version": target_policy["policy_version"],
            "policy_hash": f"sha256:{target_policy['_policy_hash']}",
        },
        "original_decision": {
            "decision": original_receipt["decision"],
            "lifecycle_status": original_receipt["lifecycle_status"],
            "effect_permitted": original_receipt["effect_permitted"],
            "reason_code": original_receipt["reason_code"],
            "policy_version": original_receipt["policy_version"],
        },
        "replay_decision": {
            "decision": replay_dec["decision"],
            "lifecycle_status": replay_dec["lifecycle_status"],
            "effect_permitted": replay_dec["effect_permitted"],
            "reason_code": replay_dec["reason_code"],
            "policy_version": target_policy["policy_version"],
            "explanation": replay_dec["explanation"],
        },
        "replay_evidence_summary": {
            "complete_under_target_policy": replay_ev["complete_under_policy"],
            "missing_refs_under_target_policy": replay_ev["missing_refs_under_policy"],
        },
        "replay_authority_summary": {
            "approver_role": replay_auth["approver_role"],
            "target_in_scope": replay_auth["target_in_scope"],
            "effect_in_role_scope": replay_auth["effect_in_role_scope"],
            "role_meets_minimum": replay_auth["role_meets_minimum"],
            "exact_role_requirement_satisfied": replay_auth["exact_role_requirement_satisfied"],
            "dual_control_required": replay_auth["dual_control_required"],
            "dual_control_present": replay_auth["dual_control_present"],
        },
        "outcome_changed": drift_class != "NO_OUTCOME_CHANGE",
        "drift_class": drift_class,
        "effect_record_existed_before_replay": effect_before,
        "effect_record_exists_after_replay": effect_after,
        "effect_record_mutated": effect_record_mutated,
        "replay_lifecycle": [
            "ORIGINAL_RECORD_LOADED",
            "ORIGINAL_INTEGRITY_VERIFIED",
            "TARGET_POLICY_LOADED",
            "FROZEN_EVIDENCE_REEVALUATED",
            "DRIFT_CLASSIFIED",
            "NO_RETROACTIVE_EFFECT_MUTATION",
            "REPLAY_REPORT_WRITTEN",
        ],
        "replay_decision_receipt_hash": f"sha256:{sha_obj(replay_receipt)}",
        "governance_note": "Replay is a comparison result. It does not create, delete, or modify the original downstream effect record.",
    }
    case_out = out_dir / req["case_id"]
    case_out.mkdir(parents=True, exist_ok=True)
    write_json(case_out / "policy_replay_report.json", report)
    return report


def replay_suite(runs_dir: Path, target_policy_path: Path, out_dir: Path) -> list[dict[str, Any]]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target_policy = load_policy(target_policy_path)
    reports = [replay_case(d, target_policy, out_dir) for d in sorted(p for p in runs_dir.iterdir() if p.is_dir())]
    write_json(
        out_dir / "_replay_index.json",
        {
            "record_type": "policy_replay_index",
            "target_policy_version": target_policy["policy_version"],
            "reports": [
                {
                    "case_id": r["case_id"],
                    "drift_class": r["drift_class"],
                    "outcome_changed": r["outcome_changed"],
                    "effect_record_mutated": r["effect_record_mutated"],
                }
                for r in reports
            ],
        },
    )
    if any(r["effect_record_mutated"] for r in reports):
        raise RuntimeError("Replay mutated an original effect record")
    return reports
