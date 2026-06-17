"""Hashing and repo-anchored manifest-signing helpers for the public proof."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import List

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


ROOT_DIR = Path(__file__).resolve().parents[2]
HASHED_SUFFIXES = {".json", ".yml", ".yaml"}
MANIFEST_NAME = "artifact_hashes.sha256.txt"
MANIFEST_SIGNATURE_NAME = "artifact_hashes.sha256.txt.sig"
ROOT_MANIFEST_PUBLIC_KEY_NAME = "MANIFEST_PUBLIC_KEY.pem"
ROOT_MANIFEST_PUBLIC_KEY_PATH = ROOT_DIR / ROOT_MANIFEST_PUBLIC_KEY_NAME
DEMO_MANIFEST_PRIVATE_KEY_PATH = ROOT_DIR / "fixtures" / "manifest_demo_private_key.pem"
# Deprecated v0.2.1 per-run key name. The verifier no longer trusts this file;
# if it is present, it must match the repo-root public key byte-for-byte.
MANIFEST_PUBLIC_KEY_NAME = "manifest_public_key.pem"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for one file."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def write_hash_manifest(run_dir: Path) -> bytes:
    """Write artifact_hashes.sha256.txt for one run directory and return bytes."""

    run_dir.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []

    artifact_paths = [
        path
        for path in sorted(run_dir.iterdir())
        if path.is_file() and path.suffix in HASHED_SUFFIXES
    ]

    for path in artifact_paths:
        file_hash = sha256_file(path)
        lines.append(f"{file_hash}  {path.name}")

    manifest_text = "\n".join(lines) + "\n"
    manifest_path = run_dir / MANIFEST_NAME
    manifest_bytes = manifest_text.encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    return manifest_bytes


def write_signed_hash_manifest(
    run_dir: Path,
    *,
    private_key_path: Path = DEMO_MANIFEST_PRIVATE_KEY_PATH,
) -> None:
    """Write local hashes, then sign the manifest with the repo fixture key.

    The verifier trusts the repo-root ``MANIFEST_PUBLIC_KEY.pem`` rather than a
    public key emitted beside the artifacts. This gives the public preview a
    real repo-level trust anchor for detecting run-directory tampering. It is
    still a demo fixture key, not an external timestamp, transparency log,
    third-party attestation, or production signing root.
    """

    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_bytes = write_hash_manifest(run_dir)

    private_key = serialization.load_pem_private_key(
        private_key_path.read_bytes(),
        password=None,
    )

    signature = private_key.sign(
        manifest_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    (run_dir / MANIFEST_SIGNATURE_NAME).write_text(
        base64.b64encode(signature).decode("ascii") + "\n",
        encoding="utf-8",
    )


def verify_hash_manifest_signature(
    run_dir: Path,
    *,
    public_key_path: Path = ROOT_MANIFEST_PUBLIC_KEY_PATH,
) -> bool:
    """Return True when the manifest signature verifies against repo root."""

    manifest_path = run_dir / MANIFEST_NAME
    signature_path = run_dir / MANIFEST_SIGNATURE_NAME

    if not manifest_path.exists() or not signature_path.exists() or not public_key_path.exists():
        return False

    root_public_key_bytes = public_key_path.read_bytes()
    per_run_public_key_path = run_dir / MANIFEST_PUBLIC_KEY_NAME
    if per_run_public_key_path.exists() and per_run_public_key_path.read_bytes() != root_public_key_bytes:
        return False

    public_key = serialization.load_pem_public_key(root_public_key_bytes)
    signature = base64.b64decode(signature_path.read_text(encoding="utf-8"))

    try:
        public_key.verify(
            signature,
            manifest_path.read_bytes(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except Exception:
        return False
    return True
