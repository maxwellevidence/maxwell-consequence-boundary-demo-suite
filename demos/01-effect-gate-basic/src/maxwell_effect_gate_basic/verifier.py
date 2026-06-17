from __future__ import annotations

from pathlib import Path
from typing import Any

from .paths import read_json, sha256_file, sha256_json, write_json
from .time_utils import utc_now


class VerificationError(RuntimeError):
    """Raised when a generated artifact set fails verification."""


def verify_run(run_dir: Path, write_report: bool = True) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    manifest_path = run_dir / "manifest.json"
    decision_path = run_dir / "decision_receipt.json"
    effect_path = run_dir / "effect_record.json"
    no_effect_path = run_dir / "NO_EFFECT_CREATED.txt"

    if not manifest_path.exists():
        raise VerificationError(f"Missing manifest: {manifest_path}")

    manifest = read_json(manifest_path)
    add("manifest_exists", True)

    for entry in manifest.get("files", []):
        rel = entry.get("path")
        expected = entry.get("sha256")
        path = run_dir / str(rel)
        if not path.exists():
            add(f"file_exists:{rel}", False, "manifest-bound file is missing")
            continue
        actual = sha256_file(path)
        add(f"hash_matches:{rel}", actual == expected, "" if actual == expected else "hash mismatch")

    if not decision_path.exists():
        add("decision_receipt_exists", False, "decision_receipt.json is missing")
        return _finish(run_dir, checks, write_report)

    decision = read_json(decision_path)
    add("decision_receipt_exists", True)

    effect_permitted = bool(decision.get("effect_permitted"))
    if effect_permitted:
        add("effect_record_required", effect_path.exists(), "effect_permitted=true")
        add("no_effect_marker_absent", not no_effect_path.exists())
    else:
        add("effect_record_absent", not effect_path.exists(), "effect_permitted=false")
        add("no_effect_marker_exists", no_effect_path.exists(), "effect_permitted=false")

    if effect_path.exists():
        effect_record = read_json(effect_path)
        expected = sha256_json(decision)
        actual = effect_record.get("decision_receipt_sha256")
        add(
            "effect_bound_to_decision_receipt",
            actual == expected,
            "" if actual == expected else "effect record is not bound to current decision receipt",
        )

    report = _finish(run_dir, checks, write_report)
    if not report["verified"]:
        failures = [check for check in checks if not check["ok"]]
        failure_text = "; ".join(f"{item['name']}={item['detail']}" for item in failures)
        raise VerificationError(f"Verification failed for {run_dir}: {failure_text}")
    return report


def verify_all(runs_dir: Path) -> list[dict[str, Any]]:
    if not runs_dir.exists():
        raise VerificationError(f"Runs directory does not exist: {runs_dir}")
    reports = []
    for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
        if (run_dir / "manifest.json").exists():
            reports.append(verify_run(run_dir))
    if not reports:
        raise VerificationError(f"No run directories found under: {runs_dir}")
    return reports


def _finish(run_dir: Path, checks: list[dict[str, Any]], write_report: bool) -> dict[str, Any]:
    decision = read_json(run_dir / "decision_receipt.json") if (run_dir / "decision_receipt.json").exists() else {}
    report = {
        "schema": "maxwell.demo.verification_report.v0.1",
        "verified_at": utc_now(),
        "case_id": decision.get("case_id", run_dir.name),
        "run_dir": run_dir.name,
        "verified": all(check["ok"] for check in checks),
        "checks": checks,
        "effect_permitted": bool(decision.get("effect_permitted")),
    }
    if write_report:
        write_json(run_dir / "verification_report.json", report)
    return report
