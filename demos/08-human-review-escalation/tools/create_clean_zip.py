from __future__ import annotations

import sys
import zipfile
from pathlib import Path

EXCLUDE_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "build",
    "dist",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log"}
EXCLUDE_FILES = {".DS_Store", ".env"}
EXCLUDE_PREFIXES = {"artifacts/runs/"}


def should_include(root: Path, path: Path) -> bool:
    rel = path.relative_to(root)
    rel_text = rel.as_posix()
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.name in EXCLUDE_FILES:
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if any(rel_text.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return False
    if ".egg-info" in rel_text:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 2:
        print("Usage: create_clean_zip.py <root> <zip_out>")
        return 2
    root = Path(argv[0]).resolve()
    zip_out = Path(argv[1]).resolve()
    if zip_out.exists():
        zip_out.unlink()
    zip_out.parent.mkdir(parents=True, exist_ok=True)
    base = root.name
    with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file() and should_include(root, path):
                zf.write(path, Path(base) / path.relative_to(root))
    print(f"Created {zip_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
