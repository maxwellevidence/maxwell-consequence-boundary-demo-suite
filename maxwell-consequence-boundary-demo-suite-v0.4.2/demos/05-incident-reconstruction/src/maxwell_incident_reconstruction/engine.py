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
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


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
    return data


def _risk_value(policy: dict[str, Any], value: str | None) -> int:
    return int((policy.get("risk_order") or {}).get(str(value or "").lower(), 999))


def evidence_snapshot(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    refs = list((req.get("evidence") or {}).get("refs") or [])
    required = list(policy.get("required_evidence_refs") or [])
    missing = sorted(set(required) - set(refs))
    return {
        "record_type": "evidence_snapshot",
        "case_id": req["case_id"],
        "evidence_refs": refs,
        "required_refs": required,
        "missing_refs": missing,
        "complete": not missing,
        "captured_at": (req.get("evidence") or {}).get("captured_at"),
    }


def authority_snapshot(req: dict[str, Any]) -> dict[str, Any]:
    auth = req.get("authority") or {}
    action = req["proposed_action"]
    systems = list(auth.get("authorized_systems") or [])
    return {
        "record_type": "authority_snapshot",
        "case_id": req["case_id"],
        "actor_id": auth.get("actor_id"),
        "approver_id": auth.get("approver_id"),
        "approval_chain": list(auth.get("approval_chain") or []),
        "authorized_systems": systems,
        "target_system": action.get("target_system"),
        "target_in_scope": action.get("target_system") in set(systems),
        "can_commit_effect": bool(auth.get("can_commit_effect")),
        "authority_present": bool(auth.get("approver_id") and auth.get("can_commit_effect")),
    }


def evaluate(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    action = req["proposed_action"]
    auth = authority_snapshot(req)
    evidence = evidence_snapshot(req, policy)
    reason = policy["reason_codes"]

    def decision(name: str, lifecycle: str, permitted: bool, review: bool, code: str, explanation: str) -> dict[str, Any]:
        return {
            "decision": name,
            "lifecycle_status": lifecycle,
            "effect_permitted": permitted,
            "review_required": review,
            "reason_code": code,
            "explanation": explanation,
        }

    if action.get("requested_effect") not in set(policy.get("allowed_effect_types") or []):
        return decision("block", "effect_suppressed", False, False, reason["block_forbidden_effect"], "Requested effect type is not permitted by demo policy.")
    if not auth["authority_present"]:
        return decision("block", "effect_suppressed", False, False, reason["block_missing_authority"], "No valid authority context supports downstream effect.")
    if not auth["target_in_scope"]:
        return decision("block", "effect_suppressed", False, False, reason["block_scope_violation"], "Target system is outside the authority scope.")
    if not evidence["complete"]:
        return decision("review", "review_routed", False, True, "INCIDENT_REQUIRED_EVIDENCE_MISSING", "Required evidence references are missing, so reconstruction would be incomplete.")
    if req.get("policy_context") in set(policy.get("stale_policy_versions") or []):
        return decision("review", "review_routed", False, True, reason["review_stale_policy_context"], "Request carries stale policy context and must be reviewed.")
    if _risk_value(policy, action.get("risk_level")) >= _risk_value(policy, policy.get("review_required_risk_at_or_above")):
        return decision("review", "review_routed", False, True, reason["review_high_risk"], "Risk level requires controlled review before effect.")
    return decision("allow", "effect_committed", True, False, reason["allow"], "Evidence, authority, scope, and risk requirements are satisfied.")


def build_receipt(req: dict[str, Any], policy: dict[str, Any], ev: dict[str, Any], au: dict[str, Any], dec: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "decision_receipt",
        "case_id": req["case_id"],
        "action_id": req["proposed_action"]["action_id"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "request_policy_context": req.get("policy_context"),
        "evaluated_at": policy.get("evaluation_time"),
        "evidence_snapshot_hash": f"sha256:{sha_obj(ev)}",
        "authority_snapshot_hash": f"sha256:{sha_obj(au)}",
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
    manifest = read_json(run_dir / "manifest.json") if (run_dir / "manifest.json").exists() else {"files": []}
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
    report = {"record_type": "verification_report", "case_id": run_dir.name, "verified": not errors, "tamper_detected": bool(errors), "errors": errors, "checked_files": checked}
    if write_report:
        write_json(run_dir / "verification_report.json", report)
    return report


def reconstruct(run_dir: Path, write_to: Path | None = None) -> dict[str, Any]:
    req = read_json(run_dir / "input_request.json")
    ev = read_json(run_dir / "evidence_snapshot.json")
    au = read_json(run_dir / "authority_snapshot.json")
    rec = read_json(run_dir / "decision_receipt.json")
    ver = verify_run(run_dir, write_report=False) if (run_dir / "manifest.json").exists() else {"verified": None, "tamper_detected": None, "errors": ["manifest missing"]}
    rep = {
        "record_type": "reconstruction_report",
        "case_id": req["case_id"],
        "proposed_action": req["proposed_action"],
        "evidence_summary": {"complete": ev["complete"], "missing_refs": ev["missing_refs"]},
        "authority_summary": {"authority_present": au["authority_present"], "target_in_scope": au["target_in_scope"], "approver_id": au.get("approver_id")},
        "decision_summary": {"decision": rec["decision"], "lifecycle_status": rec["lifecycle_status"], "reason_code": rec["reason_code"], "explanation": rec["explanation"], "policy_version": rec["policy_version"], "request_policy_context": rec.get("request_policy_context")},
        "effect_status": {"effect_record_exists": (run_dir / "effect_record.json").exists(), "review_ticket_exists": (run_dir / "review_ticket.json").exists(), "suppression_notice_exists": (run_dir / "suppression_notice.json").exists(), "no_effect_marker_exists": (run_dir / "NO_EFFECT_CREATED.txt").exists()},
        "integrity_status": {"verified": ver["verified"], "tamper_detected": ver["tamper_detected"], "errors": ver["errors"]},
    }
    if write_to is not None:
        write_json(write_to, rep)
    return rep


def run_case(input_path: Path, out_dir: Path, policy: dict[str, Any]) -> dict[str, Any]:
    req = read_json(input_path)
    run_dir = out_dir / req["case_id"]
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    ev = evidence_snapshot(req, policy)
    au = authority_snapshot(req)
    dec = evaluate(req, policy)
    rec = build_receipt(req, policy, ev, au, dec)
    write_json(run_dir / "input_request.json", req)
    write_json(run_dir / "evidence_snapshot.json", ev)
    write_json(run_dir / "authority_snapshot.json", au)
    write_json(run_dir / "decision_receipt.json", rec)
    if dec["effect_permitted"]:
        write_json(run_dir / "effect_record.json", {"record_type": "effect_record", "case_id": req["case_id"], "action_id": req["proposed_action"]["action_id"], "effect_type": req["proposed_action"]["requested_effect"], "target_system": req["proposed_action"]["target_system"], "decision_receipt_hash": f"sha256:{sha_obj(rec)}", "synthetic_no_real_execution": True})
    else:
        (run_dir / "NO_EFFECT_CREATED.txt").write_text("No downstream effect was created.\n", encoding="utf-8")
        if dec["review_required"]:
            write_json(run_dir / "review_ticket.json", {"record_type": "review_ticket", "case_id": req["case_id"], "reason_code": dec["reason_code"], "review_queue": "incident_governance_review_queue", "effect_created": False})
        else:
            write_json(run_dir / "suppression_notice.json", {"record_type": "suppression_notice", "case_id": req["case_id"], "reason_code": dec["reason_code"], "effect_created": False})
    write_json(run_dir / "timeline_event.json", {"record_type": "timeline_event", "case_id": req["case_id"], "event_sequence": ["PROPOSED", "EVIDENCE_CAPTURED", "AUTHORITY_EVALUATED", "DECISION_RECORDED", dec["lifecycle_status"].upper(), "RECONSTRUCTABLE_RECORD_CREATED"], "effect_created": dec["effect_permitted"]})
    reconstruct(run_dir, write_to=run_dir / "reconstruction_report.json")
    write_manifest(run_dir)
    verify_run(run_dir, write_report=True)
    return {"case_id": req["case_id"], "lifecycle_status": dec["lifecycle_status"], "effect_created": dec["effect_permitted"], "verified": True}


def run_suite(input_dir: Path, out_dir: Path, policy_path: Path) -> list[dict[str, Any]]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    policy = load_policy(policy_path)
    results = [run_case(p, out_dir, policy) for p in sorted(input_dir.glob("*.json"))]
    write_json(out_dir / "_suite_summary.json", {"runs": results})
    return results


def verify_suite(runs_dir: Path) -> list[dict[str, Any]]:
    return [verify_run(d, True) for d in sorted(p for p in runs_dir.iterdir() if p.is_dir())]


def reconstruct_suite(runs_dir: Path, out_dir: Path) -> list[dict[str, Any]]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    for d in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        report = reconstruct(d, write_to=out_dir / f"{d.name}_reconstruction_report.json")
        reports.append(report)
    write_json(out_dir / "reconstruction_index.json", {"record_type": "reconstruction_index", "reports": [{"case_id": r["case_id"], "reason_code": r["decision_summary"]["reason_code"], "verified": r["integrity_status"]["verified"], "effect_record_exists": r["effect_status"]["effect_record_exists"]} for r in reports]})
    return reports


def tamper_lab(runs_dir: Path, out_dir: Path, seed: str = "05_tamper_detection_lab_seed") -> dict[str, Any]:
    source = runs_dir / seed
    if not source.exists():
        raise FileNotFoundError("run make demo before tamper-demo")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{seed}_tampered"
    shutil.copytree(source, target)
    receipt = read_json(target / "decision_receipt.json")
    receipt["tampered_marker"] = True
    write_json(target / "decision_receipt.json", receipt)
    report = verify_run(target, write_report=True)
    result = {"record_type": "tamper_detection_report", "seed_case": seed, "tampered_run": target.name, "tamper_detected": report["tamper_detected"], "verified": report["verified"], "errors": report["errors"]}
    write_json(out_dir / "tamper_detection_report.json", result)
    if not result["tamper_detected"]:
        raise RuntimeError("tamper was not detected")
    return result
