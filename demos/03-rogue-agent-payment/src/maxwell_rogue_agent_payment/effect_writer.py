from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .authority_context import build_authority_context
from .decision_receipt import build_decision_receipt
from .evidence_bundle import build_evidence_bundle
from .paths import read_json, safe_case_name, sha256_file, sha256_json, write_json
from .policy_engine import evaluate_policy, load_policy
from .time_utils import utc_now


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _build_payment_effect_record(
    case: dict[str, Any], decision_receipt: dict[str, Any]
) -> dict[str, Any]:
    payment = _as_dict(case.get("payment_request"))
    requested_effect = _as_dict(case.get("requested_effect"))
    record = {
        "schema": "maxwell.payment_demo.payment_effect_record.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "effect_type": requested_effect.get("effect_type", "payment.release"),
        "target_system": requested_effect.get("target_system", "synthetic_accounts_payable"),
        "committed_at": utc_now(),
        "decision_receipt_id": decision_receipt.get("decision_receipt_id"),
        "decision_receipt_sha256": sha256_json(decision_receipt),
        "reason_code": decision_receipt.get("reason_code"),
        "payment_commitment": {
            "invoice_id": payment.get("invoice_id"),
            "vendor_id": payment.get("vendor_id"),
            "amount_usd": payment.get("amount_usd"),
            "currency": payment.get("currency", "USD"),
            "payment_method": payment.get("payment_method"),
            "synthetic_no_real_payment": True,
        },
        "public_preview_note": "Synthetic payment effect record only; no real downstream payment occurred.",
    }
    record["payment_effect_record_id"] = f"sha256:{sha256_json(record)}"
    return record


def _build_review_ticket(
    case: dict[str, Any], decision_receipt: dict[str, Any]
) -> dict[str, Any]:
    payment = _as_dict(case.get("payment_request"))
    ticket = {
        "schema": "maxwell.payment_demo.review_ticket.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "review_route": decision_receipt.get("review_route"),
        "reason_code": decision_receipt.get("reason_code"),
        "invoice_id": payment.get("invoice_id"),
        "vendor_id": payment.get("vendor_id"),
        "amount_usd": payment.get("amount_usd"),
        "created_at": utc_now(),
        "decision_receipt_id": decision_receipt.get("decision_receipt_id"),
        "decision_receipt_sha256": sha256_json(decision_receipt),
        "public_preview_note": "Synthetic review ticket only; no real workflow queue was contacted.",
    }
    ticket["review_ticket_id"] = f"sha256:{sha256_json(ticket)}"
    return ticket


def _build_suppression_notice(
    case: dict[str, Any], decision_receipt: dict[str, Any]
) -> dict[str, Any]:
    notice = {
        "schema": "maxwell.payment_demo.suppression_notice.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "reason_code": decision_receipt.get("reason_code"),
        "authority_basis": decision_receipt.get("authority_basis"),
        "risk_signal": decision_receipt.get("risk_signal"),
        "created_at": utc_now(),
        "decision_receipt_id": decision_receipt.get("decision_receipt_id"),
        "decision_receipt_sha256": sha256_json(decision_receipt),
        "public_preview_note": "Synthetic suppression notice only; no real downstream payment effect occurred.",
    }
    notice["suppression_notice_id"] = f"sha256:{sha256_json(notice)}"
    return notice


def _write_manifest(run_dir: Path) -> dict[str, Any]:
    files = []
    for path in sorted(run_dir.iterdir()):
        if path.name in {"manifest.json", "verification_report.json"} or not path.is_file():
            continue
        files.append({"path": path.name, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    manifest = {
        "schema": "maxwell.payment_demo.manifest.v0.1",
        "manifest_version": "payment-demo-manifest-v0.1.0",
        "created_at": utc_now(),
        "files": files,
    }
    write_json(run_dir / "manifest.json", manifest)
    return manifest


def run_case(input_path: Path, policy_path: Path, out_root: Path) -> dict[str, Any]:
    case = read_json(input_path)
    case_id = safe_case_name(str(case.get("case_id") or input_path.stem))
    run_dir = out_root / case_id

    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    policy = load_policy(policy_path)
    evidence_bundle = build_evidence_bundle(case)
    authority_context = build_authority_context(case)
    decision = evaluate_policy(case, evidence_bundle, authority_context, policy)
    decision_receipt = build_decision_receipt(case, evidence_bundle, authority_context, decision, policy)

    write_json(run_dir / "input_request.json", case)
    write_json(run_dir / "payment_evidence_bundle.json", evidence_bundle)
    write_json(run_dir / "authority_context.json", authority_context)
    write_json(run_dir / "decision_receipt.json", decision_receipt)

    if decision.effect_permitted:
        effect_record = _build_payment_effect_record(case, decision_receipt)
        write_json(run_dir / "payment_effect_record.json", effect_record)
    else:
        marker = run_dir / "NO_PAYMENT_EFFECT_CREATED.txt"
        marker.write_text(
            "No downstream payment effect record was created because policy did not permit effect.\n"
            f"Reason code: {decision.reason_code}\n",
            encoding="utf-8",
        )
        if decision.lifecycle_state == "PAYMENT_REVIEW_ROUTED":
            write_json(run_dir / "review_ticket.json", _build_review_ticket(case, decision_receipt))
        if decision.lifecycle_state == "PAYMENT_EFFECT_SUPPRESSED":
            write_json(run_dir / "suppression_notice.json", _build_suppression_notice(case, decision_receipt))

    manifest = _write_manifest(run_dir)
    return {
        "case_id": case_id,
        "run_dir": str(run_dir),
        "outcome": decision.outcome,
        "lifecycle_state": decision.lifecycle_state,
        "reason_code": decision.reason_code,
        "effect_permitted": decision.effect_permitted,
        "manifest_file_count": len(manifest["files"]),
    }


def run_all(input_dir: Path, policy_path: Path, out_root: Path) -> list[dict[str, Any]]:
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    input_paths = sorted(input_dir.glob("*.json"))
    if not input_paths:
        raise ValueError(f"No JSON input files found under {input_dir}")
    return [run_case(path, policy_path, out_root) for path in input_paths]
