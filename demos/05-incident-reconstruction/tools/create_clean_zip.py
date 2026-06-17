from __future__ import annotations

import sys
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv", "build", "dist", ".git"}
EXCLUDE_NAMES = {".env", ".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log"}


def exclude(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    rel_posix = rel.as_posix()
    parts = set(rel.parts)
    if path.name in EXCLUDE_NAMES or path.suffix in EXCLUDE_SUFFIXES:
        return True
    if parts & EXCLUDE_DIRS:
        return True
    if rel_posix.startswith("artifacts/runs/") or rel_posix.startswith("artifacts/reconstruction/") or rel_posix.startswith("artifacts/tamper_demo/"):
        return True
    if ".egg-info/" in rel_posix or rel_posix.endswith(".egg-info"):
        return True
    return False


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: create_clean_zip.py <root> [zip_out]")
        return 2
    root = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else root.parent / f"{root.name}.zip"
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file() and not exclude(path, root):
                archive.write(path, Path(root.name) / path.relative_to(root))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
