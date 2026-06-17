from pathlib import Path

from maxwell_effect_gate_basic.effect_writer import run_case
from maxwell_effect_gate_basic.paths import read_json

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "effect_gate_basic_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_no_authority_no_downstream_effect_record(tmp_path):
    result = run_case(INPUTS / "03_missing_authority_context.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    receipt = read_json(run_dir / "decision_receipt.json")

    assert receipt["effect_permitted"] is False
    assert receipt["reason_code"] == "EFFECT_GATE_AUTHORITY_CONTEXT_MISSING"
    assert not (run_dir / "effect_record.json").exists()
    assert (run_dir / "NO_EFFECT_CREATED.txt").exists()
