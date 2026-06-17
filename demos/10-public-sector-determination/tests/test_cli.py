from __future__ import annotations

from pathlib import Path

from maxwell_public_sector_determination.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_cli_demo_and_verify(tmp_path: Path) -> None:
    out = tmp_path / "runs"
    assert main([
        "demo",
        "--inputs",
        str(ROOT / "examples" / "demo_inputs"),
        "--policy",
        str(ROOT / "policies" / "public_sector_determination_policy.yml"),
        "--out",
        str(out),
    ]) == 0
    assert main(["verify", "--runs", str(out)]) == 0
