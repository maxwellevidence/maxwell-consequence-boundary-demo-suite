from __future__ import annotations

from pathlib import Path

from maxwell_incident_reconstruction.engine import run_suite, verify_suite

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "examples" / "adversarial_inputs"
POLICY = ROOT / "policies/incident_reconstruction_policy.yml"
EFFECT_FILE = "effect_record.json"
NO_EFFECT_FILE = "NO_EFFECT_CREATED.txt"


def test_adversarial_corpus_fails_closed(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    rows = run_suite(INPUTS, runs, POLICY)
    assert len(rows) >= 3
    reports = verify_suite(runs)
    assert all(report.get("verified") for report in reports)
    for run_dir in sorted(runs.iterdir()):
        if not run_dir.is_dir():
            continue
        assert not (run_dir / EFFECT_FILE).exists()
        assert (run_dir / NO_EFFECT_FILE).exists()
