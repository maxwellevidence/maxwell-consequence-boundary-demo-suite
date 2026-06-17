from __future__ import annotations

from typing import Any

from .paths import sha256_json
from .time_utils import utc_now


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _evidence_types(evidence_refs: list[Any]) -> list[str]:
    types: list[str] = []
    for ref in evidence_refs:
        if isinstance(ref, dict) and ref.get("type"):
            types.append(str(ref["type"]))
    return sorted(set(types))


def build_evidence_bundle(case: dict[str, Any]) -> dict[str, Any]:
    """Create a public-safe payment evidence bundle for a proposed payment action."""
    payment = _as_dict(case.get("payment_request"))
    evidence_refs = _as_list(case.get("evidence_refs"))
    evidence_types = _evidence_types(evidence_refs)

    bundle = {
        "schema": "maxwell.payment_demo.evidence_bundle.v0.1",
        "case_id": case.get("case_id", "unknown_case"),
        "invoice_id": payment.get("invoice_id"),
        "amount_usd": payment.get("amount_usd"),
        "currency": payment.get("currency", "USD"),
        "vendor_id": payment.get("vendor_id"),
        "vendor_status": payment.get("vendor_status"),
        "vendor_bank_change": bool(payment.get("vendor_bank_change", False)),
        "payment_method": payment.get("payment_method"),
        "risk_level": case.get("risk_level"),
        "evidence_count": len(evidence_refs),
        "evidence_types": evidence_types,
        "evidence_refs": evidence_refs,
        "created_at": utc_now(),
        "public_preview_note": "Synthetic payment evidence bundle only; no real invoice or payment data.",
    }
    bundle["bundle_id"] = f"sha256:{sha256_json(bundle)}"
    return bundle
