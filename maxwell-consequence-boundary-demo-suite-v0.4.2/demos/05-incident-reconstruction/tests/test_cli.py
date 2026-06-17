from pathlib import Path

from maxwell_incident_reconstruction.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_flow(tmp_path):
    runs = tmp_path / "runs"
    lab = tmp_path / "lab"
    assert main(["run-suite", "--input-dir", str(ROOT / "examples/demo_inputs"), "--out-dir", str(runs), "--policy", str(ROOT / "policies/incident_reconstruction_policy.yml")]) == 0
    assert main(["verify-suite", "--runs-dir", str(runs)]) == 0
    assert main(["reconstruct-suite", "--runs-dir", str(runs)]) == 0
    assert main(["tamper-lab", "--runs-dir", str(runs), "--out-dir", str(lab)]) == 0
