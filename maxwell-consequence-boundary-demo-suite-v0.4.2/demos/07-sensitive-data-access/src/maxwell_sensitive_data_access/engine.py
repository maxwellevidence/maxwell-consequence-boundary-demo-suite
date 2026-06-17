from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

EXCLUDE_FROM_MANIFEST = {"manifest.json", "verification_report.json"}
EFFECT_FILE = "data_access_effect_record.json"
NO_EFFECT_FILE = "NO_DATA_ACCESS_EFFECT_CREATED.txt"


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


def rank_data_class(policy: dict[str, Any], value: str | None) -> int:
    return int((policy.get("data_class_order") or {}).get(str(value or "").lower(), 999))


def _text_blob(req: dict[str, Any]) -> str:
    access = req.get("requested_access") or {}
    llm = req.get("llm_output") or {}
    parts = [
        access.get("user_instruction"),
        access.get("purpose"),
        llm.get("recommendation"),
        llm.get("instruction_trace"),
    ]
    return " ".join(str(p or "") for p in parts).lower()


def prompt_injection_detected(req: dict[str, Any], policy: dict[str, Any]) -> bool:
    llm = req.get("llm_output") or {}
    if bool(llm.get("prompt_injection_detected")):
        return True
    blob = _text_blob(req)
    return any(str(indicator).lower() in blob for indicator in policy.get("prompt_injection_indicators") or [])


def evidence_bundle(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    evidence = req.get("evidence") or {}
    access = req.get("requested_access") or {}
    refs = list(evidence.get("refs") or [])
    required = list(policy.get("required_evidence_refs") or [])
    missing = sorted(set(required) - set(refs))
    purpose = access.get("purpose") or evidence.get("business_purpose")
    return {
        "record_type": "data_evidence_bundle",
        "case_id": req["case_id"],
        "access_id": access.get("access_id"),
        "evidence_refs": refs,
        "required_refs": required,
        "missing_refs": missing,
        "evidence_complete": not missing,
        "business_purpose": purpose,
        "business_purpose_present": bool(purpose),
        "legal_basis": evidence.get("legal_basis"),
        "legal_basis_present": bool(evidence.get("legal_basis")),
        "data_minimization": bool(evidence.get("data_minimization")),
        "captured_at": evidence.get("captured_at"),
        "prompt_injection_detected": prompt_injection_detected(req, policy),
        "instruction_trace_preserved": bool((req.get("llm_output") or {}).get("instruction_trace")),
    }


def authority_context(req: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    actor = req.get("actor") or {}
    access = req.get("requested_access") or {}
    evidence = req.get("evidence") or {}
    role = actor.get("role")
    dataset = access.get("dataset")
    requested_effect = access.get("requested_effect")
    requested_fields = list(access.get("requested_fields") or [])
    target_system = access.get("target_system")
    purpose = access.get("purpose") or evidence.get("business_purpose")
    query_scope = access.get("query_scope")

    role_profile = dict((policy.get("roles") or {}).get(role) or {})
    dataset_profile = dict((policy.get("datasets") or {}).get(dataset) or {})
    data_class = access.get("data_class") or dataset_profile.get("data_class")
    max_data_class = role_profile.get("max_data_class")

    role_allowed_datasets = set(role_profile.get("allowed_datasets") or [])
    role_approved_purposes = set(role_profile.get("approved_purposes") or [])
    role_allowed_targets = set(role_profile.get("allowed_target_systems") or [])
    dataset_allowed_roles = set(dataset_profile.get("allowed_roles") or [])
    dataset_approved_purposes = set(dataset_profile.get("approved_purposes") or [])
    restricted_fields = set(policy.get("restricted_fields") or [])
    requested_restricted_fields = sorted(restricted_fields.intersection(requested_fields))
    restricted_field_roles = set(policy.get("restricted_field_roles") or [])

    legal_basis_required = bool(dataset_profile.get("legal_basis_required"))
    restricted_field_approval_present = bool(evidence.get("restricted_field_approval"))
    restricted_fields_allowed = not requested_restricted_fields or (
        role in restricted_field_roles and restricted_field_approval_present
    )

    return {
        "record_type": "authority_context",
        "case_id": req["case_id"],
        "actor_id": actor.get("actor_id"),
        "actor_role": role,
        "role_known": bool(role_profile),
        "role_can_request_access": bool(role_profile.get("can_request_access")),
        "dataset": dataset,
        "dataset_known": bool(dataset_profile),
        "requested_effect": requested_effect,
        "target_system": target_system,
        "target_in_role_scope": target_system in role_allowed_targets,
        "data_class": data_class,
        "max_data_class_for_role": max_data_class,
        "data_class_within_clearance": rank_data_class(policy, data_class)
        <= rank_data_class(policy, max_data_class),
        "dataset_in_role_scope": dataset in role_allowed_datasets,
        "role_allowed_by_dataset": role in dataset_allowed_roles,
        "purpose": purpose,
        "purpose_present": bool(purpose),
        "purpose_in_role_scope": purpose in role_approved_purposes,
        "purpose_in_dataset_scope": purpose in dataset_approved_purposes,
        "legal_basis_required": legal_basis_required,
        "legal_basis_present": bool(evidence.get("legal_basis")),
        "query_scope": query_scope,
        "data_minimization_satisfied": bool(evidence.get("data_minimization"))
        and query_scope not in set(policy.get("review_required_query_scopes") or []),
        "requested_fields": requested_fields,
        "requested_restricted_fields": requested_restricted_fields,
        "restricted_field_approval_present": restricted_field_approval_present,
        "restricted_fields_allowed": restricted_fields_allowed,
        "authority_present": bool(role_profile.get("can_request_access")),
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
    access = req.get("requested_access") or {}
    ev = evidence_bundle(req, policy)
    auth = authority_context(req, policy)
    reason = policy["reason_codes"]
    requested_effect = access.get("requested_effect")

    if ev["prompt_injection_detected"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_prompt_injection"],
            "Prompt-injected instructions are preserved as evidence but are not authority.",
        )
    if requested_effect not in set(policy.get("allowed_effect_types") or []):
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_forbidden_effect"],
            "Requested data effect type is not allowed by policy.",
        )
    if not ev["business_purpose_present"]:
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            reason["review_missing_purpose"],
            "The request does not include a business purpose.",
        )
    if not ev["evidence_complete"]:
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            reason["review_missing_evidence"],
            "Required data-access evidence references are missing.",
        )
    if not auth["authority_present"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_missing_authority"],
            "The actor role is missing, unknown, or lacks data-access authority.",
        )
    if not auth["dataset_known"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_dataset_scope"],
            "Requested dataset is not known to the evaluated policy.",
        )
    if not auth["data_class_within_clearance"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_classification"],
            "Requested data class exceeds the actor role's policy clearance.",
        )
    if not auth["dataset_in_role_scope"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_dataset_scope"],
            "Requested dataset is outside the actor role's authorized scope.",
        )
    if not auth["role_allowed_by_dataset"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_role_not_authorized"],
            "Actor role is not authorized for the requested dataset.",
        )
    if not auth["target_in_role_scope"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_target_system"],
            "Downstream target system is outside the actor role's authorized scope.",
        )
    if not auth["purpose_in_role_scope"] or not auth["purpose_in_dataset_scope"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_purpose_scope"],
            "The stated purpose is not approved for this role or dataset.",
        )
    if auth["legal_basis_required"] and not auth["legal_basis_present"]:
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            reason["review_legal_basis"],
            "Legal basis is required for this dataset or data class.",
        )
    if not auth["restricted_fields_allowed"]:
        return _decision(
            "suppress",
            "access_suppressed",
            False,
            False,
            reason["block_restricted_fields"],
            "The request includes restricted fields without sufficient approval.",
        )
    if not auth["data_minimization_satisfied"]:
        return _decision(
            "review",
            "review_routed",
            False,
            True,
            reason["review_minimization"],
            "The request is broad or lacks data-minimization evidence.",
        )

    return _decision(
        "grant",
        "access_effect_committed",
        True,
        False,
        reason["grant_access"],
        "Role, purpose, dataset scope, data class, evidence, and minimization are satisfied.",
    )


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
        "access_id": req["requested_access"].get("access_id"),
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


def build_effect_record(req: dict[str, Any], receipt: dict[str, Any], auth: dict[str, Any]) -> dict[str, Any]:
    access = req["requested_access"]
    rec = {
        "record_type": "data_access_effect_record",
        "case_id": req["case_id"],
        "access_id": access.get("access_id"),
        "effect_type": access.get("requested_effect"),
        "dataset": access.get("dataset"),
        "approved_fields": access.get("requested_fields") or [],
        "target_system": access.get("target_system"),
        "purpose": auth.get("purpose"),
        "data_payload_included": False,
        "effect_basis": receipt["decision_receipt_id"],
        "effect_committed": True,
        "note": "This synthetic demo records a permitted access effect; it does not return data.",
    }
    rec["effect_record_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_review_ticket(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "review_ticket",
        "case_id": req["case_id"],
        "access_id": req["requested_access"].get("access_id"),
        "review_queue": "privacy_data_access_review",
        "reason_code": receipt["reason_code"],
        "effect_created": False,
        "decision_receipt_id": receipt["decision_receipt_id"],
    }
    rec["review_ticket_id"] = f"sha256:{sha_obj(rec)}"
    return rec


def build_suppression_notice(req: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    rec = {
        "record_type": "suppression_notice",
        "case_id": req["case_id"],
        "access_id": req["requested_access"].get("access_id"),
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
    review_exists = (run_dir / "review_ticket.json").exists()
    suppression_exists = (run_dir / "suppression_notice.json").exists()

    if receipt.get("effect_permitted") and not effect_exists:
        errors.append(f"{EFFECT_FILE} missing despite effect_permitted=true")
    if receipt.get("effect_permitted") and no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} exists despite effect_permitted=true")
    if not receipt.get("effect_permitted") and effect_exists:
        errors.append(f"{EFFECT_FILE} exists despite effect_permitted=false")
    if not receipt.get("effect_permitted") and not no_effect_exists:
        errors.append(f"{NO_EFFECT_FILE} missing despite effect_permitted=false")
    if receipt.get("review_required") and not review_exists:
        errors.append("review_ticket.json missing despite review_required=true")
    if receipt.get("decision") == "suppress" and not suppression_exists:
        errors.append("suppression_notice.json missing despite decision=suppress")

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

    ev = evidence_bundle(req, policy)
    auth = authority_context(req, policy)
    dec = evaluate(req, policy)
    receipt = build_decision_receipt(req, policy, ev, auth, dec)

    write_json(run_dir / "input_request.json", req)
    write_json(run_dir / "policy_snapshot.json", policy_snapshot(policy))
    write_json(run_dir / "data_evidence_bundle.json", ev)
    write_json(run_dir / "authority_context.json", auth)
    write_json(run_dir / "decision_receipt.json", receipt)

    if receipt["effect_permitted"]:
        write_json(run_dir / EFFECT_FILE, build_effect_record(req, receipt, auth))
    else:
        (run_dir / NO_EFFECT_FILE).write_text(
            "No downstream data-access effect was created because policy-derived evidence and "
            "authority did not permit access.\n",
            encoding="utf-8",
        )
        if receipt["review_required"]:
            write_json(run_dir / "review_ticket.json", build_review_ticket(req, receipt))
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
