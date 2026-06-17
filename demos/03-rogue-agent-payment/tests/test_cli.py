from pathlib import Path

from maxwell_rogue_agent_payment.cli import main

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "payment_authority_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_cli_demo_and_verify(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    assert main(["demo", "--policy", str(POLICY), "--inputs", str(INPUTS), "--out", str(out)]) == 0
    assert main(["verify", "--runs", str(out)]) == 0
    assert (out / "01_low_risk_invoice_valid" / "payment_effect_record.json").exists()
    assert (out / "02_high_value_missing_dual_approval" / "review_ticket.json").exists()
    assert (out / "04_self_approval_attempt" / "suppression_notice.json").exists()
    assert (out / "05_prompt_injection_urgent_payment" / "NO_PAYMENT_EFFECT_CREATED.txt").exists()
