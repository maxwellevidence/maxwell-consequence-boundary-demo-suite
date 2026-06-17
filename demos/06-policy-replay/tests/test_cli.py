from pathlib import Path

from maxwell_policy_replay.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_flow(tmp_path):
    runs = tmp_path / "runs"
    replay = tmp_path / "replay"
    assert main(["run-suite", "--input-dir", str(ROOT / "examples/demo_inputs"), "--policy", str(ROOT / "policies/policy_v1.yml"), "--out-dir", str(runs)]) == 0
    assert main(["verify-suite", "--runs-dir", str(runs)]) == 0
    assert main(["replay-suite", "--runs-dir", str(runs), "--target-policy", str(ROOT / "policies/policy_v2.yml"), "--out-dir", str(replay)]) == 0
    assert (replay / "_replay_index.json").exists()
