from pathlib import Path

from maxwell_multi_agent_authority.effect_writer import run_case
from maxwell_multi_agent_authority.paths import read_json

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "multi_agent_authority_policy.yml"
INPUTS = ROOT / "examples" / "demo_inputs"


def test_task_handoff_is_not_authority_handoff_for_scope_expansion(tmp_path):
    result = run_case(INPUTS / "03_agent_expands_task_beyond_scope.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    receipt = read_json(run_dir / "decision_receipt.json")
    authority = read_json(run_dir / "authority_context.json")

    assert receipt["effect_permitted"] is False
    assert receipt["reason_code"] == "AGENT_SCOPE_EXPANSION_SUPPRESSED"
    assert authority["task_expansion_detected"] is True
    assert not (run_dir / "delegated_effect_record.json").exists()
    assert (run_dir / "NO_DELEGATED_EFFECT_CREATED.txt").exists()


def test_instruction_text_cannot_create_delegation(tmp_path):
    result = run_case(INPUTS / "06_prompt_injection_handoff_override.json", POLICY, tmp_path)
    run_dir = Path(result["run_dir"])
    receipt = read_json(run_dir / "decision_receipt.json")

    assert receipt["effect_permitted"] is False
    assert receipt["reason_code"] == "DELEGATION_PROMPT_INJECTION_SUPPRESSED"
    assert receipt["authority_basis"] == "instruction_text_cannot_create_delegation"
    assert not (run_dir / "delegated_effect_record.json").exists()
