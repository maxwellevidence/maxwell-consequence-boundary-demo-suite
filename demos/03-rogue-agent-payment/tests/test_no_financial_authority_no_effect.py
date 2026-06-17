from pathlib import Path

from maxwell_rogue_agent_payment.effect_writer import run_case
from maxwell_rogue_agent_payment.paths import read_json

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "payment_authority_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_ai_recommendation_is_not_financial_authority(tmp_path):
    result = run_case(INPUTS / "05_prompt_injection_urgent_payment.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    receipt = read_json(run_dir / "decision_receipt.json")

    assert receipt["effect_permitted"] is False
    assert receipt["reason_code"] == "PAYMENT_PROMPT_INJECTION_SUPPRESSED"
    assert receipt["authority_basis"] == "instruction_text_cannot_create_authority"
    assert not (run_dir / "payment_effect_record.json").exists()
    assert (run_dir / "NO_PAYMENT_EFFECT_CREATED.txt").exists()
    assert (run_dir / "suppression_notice.json").exists()
