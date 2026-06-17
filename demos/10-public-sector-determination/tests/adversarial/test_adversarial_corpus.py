from __future__ import annotations

from pathlib import Path

from maxwell_public_sector_determination.engine import EFFECT_FILE, NO_EFFECT_FILE, read_json, run_suite, verify_suite

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "examples" / "adversarial_inputs"
POLICY = ROOT / "policies/public_sector_determination_policy.yml"


def test_adversarial_corpus_fails_closed(tmp_path: Path) -> None:
    rows = run_suite(INPUTS, tmp_path / "runs", POLICY)
    assert len(rows) >= 3
    reports = verify_suite(tmp_path / "runs")
    assert all(report.get("verified") for report in reports)
    for run_dir in sorted((tmp_path / "runs").iterdir()):
        if not run_dir.is_dir():
            continue
        receipt = read_json(run_dir / "decision_receipt.json")
        assert receipt["effect_permitted"] is False
        assert not (run_dir / EFFECT_FILE).exists()
        assert (run_dir / NO_EFFECT_FILE).exists()
