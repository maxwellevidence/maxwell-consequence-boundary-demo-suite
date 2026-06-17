from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".venv",
    "venv",
    "build",
    "dist",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log"}
EXCLUDE_FILES = {".DS_Store", ".env"}


def should_exclude(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    rel_text = rel.as_posix()
    if path.name in EXCLUDE_FILES:
        return True
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return True
    if rel_text.startswith("artifacts/") and rel_text.endswith("_run"):
        return True
    if len(rel.parts) >= 2 and rel.parts[0] == "artifacts" and rel.parts[1].endswith("_run"):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a clean Maxwell demo ZIP.")
    parser.add_argument("root", help="Demo root folder to zip")
    parser.add_argument("zipfile", help="Output zip path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.zipfile).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_dir() or should_exclude(path, root):
                continue
            arcname = Path(root.name) / path.relative_to(root)
            zf.write(path, arcname.as_posix())

    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
