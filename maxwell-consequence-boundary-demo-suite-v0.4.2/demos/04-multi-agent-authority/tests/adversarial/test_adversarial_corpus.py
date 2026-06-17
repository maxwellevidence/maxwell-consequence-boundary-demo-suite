from __future__ import annotations

import json
from pathlib import Path

from maxwell_multi_agent_authority.cli import main

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "examples" / "adversarial_inputs"
POLICY = ROOT / "policies/multi_agent_authority_policy.yml"
EFFECT_FILE = "delegated_effect_record.json"
NO_EFFECT_FILE = "NO_DELEGATED_EFFECT_CREATED.txt"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_adversarial_corpus_fails_closed(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    assert main(["demo", "--inputs", str(INPUTS), "--policy", str(POLICY), "--out", str(out)]) == 0
    assert main(["verify", "--runs", str(out)]) == 0
    run_dirs = [path for path in sorted(out.iterdir()) if path.is_dir()]
    assert len(run_dirs) >= 3
    for run_dir in run_dirs:
        receipt = read_json(run_dir / "decision_receipt.json")
        assert receipt.get("effect_permitted") is False
        assert not (run_dir / EFFECT_FILE).exists()
        assert (run_dir / NO_EFFECT_FILE).exists()
