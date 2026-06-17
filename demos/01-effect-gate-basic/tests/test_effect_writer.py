from pathlib import Path

from maxwell_effect_gate_basic.effect_writer import run_case
from maxwell_effect_gate_basic.paths import read_json, sha256_json

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "effect_gate_basic_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_permitted_case_creates_effect_record(tmp_path):
    result = run_case(INPUTS / "01_valid_low_risk_notice.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    assert (run_dir / "effect_record.json").exists()
    assert not (run_dir / "NO_EFFECT_CREATED.txt").exists()

    receipt = read_json(run_dir / "decision_receipt.json")
    effect = read_json(run_dir / "effect_record.json")
    assert receipt["effect_permitted"] is True
    assert effect["decision_receipt_sha256"] == sha256_json(receipt)


def test_non_permitted_case_creates_no_effect_marker(tmp_path):
    result = run_case(INPUTS / "04_scope_violation_suppressed.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    assert not (run_dir / "effect_record.json").exists()
    assert (run_dir / "NO_EFFECT_CREATED.txt").exists()
