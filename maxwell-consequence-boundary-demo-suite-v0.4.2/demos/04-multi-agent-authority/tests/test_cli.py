from pathlib import Path

from maxwell_multi_agent_authority.cli import main

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "multi_agent_authority_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_cli_demo_and_verify(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    assert main(["demo", "--policy", str(POLICY), "--inputs", str(INPUTS), "--out", str(out)]) == 0
    assert main(["verify", "--runs", str(out)]) == 0
    assert (out / "01_valid_delegated_handoff" / "delegated_effect_record.json").exists()
    assert (out / "02_handoff_missing_authority_scope" / "review_ticket.json").exists()
    assert (out / "03_agent_expands_task_beyond_scope" / "suppression_notice.json").exists()
    assert (out / "05_handoff_loses_evidence_packet" / "NO_DELEGATED_EFFECT_CREATED.txt").exists()
