from pathlib import Path

from maxwell_effect_gate_basic.cli import main

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "effect_gate_basic_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_cli_demo_and_verify(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    assert main(["demo", "--policy", str(POLICY), "--inputs", str(INPUTS), "--out", str(out)]) == 0
    assert main(["verify", "--runs", str(out)]) == 0
    assert (out / "01_valid_low_risk_notice" / "effect_record.json").exists()
    assert (out / "03_missing_authority_context" / "NO_EFFECT_CREATED.txt").exists()
