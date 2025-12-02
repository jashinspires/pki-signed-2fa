"""Create the commit proof bundle required by the assignment."""
from __future__ import annotations

import logging
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import ensure_parent, settings
from app.crypto_utils import rsa_encrypt_with_public, rsa_pss_sign
from app.logger import configure_logging

PROOF_README = "/data/README_proof.txt"


def run_git_command(*args: str) -> str:
    result = subprocess.check_output(["git", *args], text=True).strip()
    return result


def write_commit_hash(path: Path) -> str:
    commit_hash = run_git_command("rev-parse", "--verify", "HEAD")
    ensure_parent(path)
    path.write_text(commit_hash, encoding="utf-8")
    return commit_hash


def write_signature(commit_hash: str) -> None:
    signature = rsa_pss_sign(settings.private_key_path(), commit_hash.encode("utf-8"))
    ensure_parent(settings.proof_sig_path)
    settings.proof_sig_path.write_bytes(signature)

    encrypted = rsa_encrypt_with_public(
        settings.instructor_public_key_path,
        signature,
    )
    settings.proof_sig_enc_path.write_text(encrypted, encoding="utf-8")


def write_readme(commit_hash: str) -> Path:
    readme_path = Path(PROOF_README)
    ensure_parent(readme_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    content = (
        "Proof Generation Summary\n"
        f"Timestamp: {timestamp}\n"
        f"Commit Hash: {commit_hash}\n"
        f"Signature: {settings.proof_sig_path}\n"
        f"Encrypted Signature: {settings.proof_sig_enc_path}\n"
        f"Instructor Public Key: {settings.instructor_public_key_path}\n"
    )
    readme_path.write_text(content, encoding="utf-8")
    return readme_path


def bundle_artifacts(paths: list[Path]) -> None:
    ensure_parent(settings.proof_tar_path)
    with tarfile.open(settings.proof_tar_path, "w:gz") as tar:
        for item in paths:
            tar.add(item, arcname=item.name)


def main() -> None:
    configure_logging()
    logger = logging.getLogger("generate_proof")

    if not settings.instructor_public_key_path.exists():
        logger.error(
            "Instructor public key missing at %s",
            settings.instructor_public_key_path,
        )
        raise SystemExit(1)

    commit_path = Path("/data/commit_hash.txt")
    commit_hash = write_commit_hash(commit_path)
    logger.info("Captured commit hash: %s", commit_hash)

    write_signature(commit_hash)
    logger.info("Signature written to %s", settings.proof_sig_path)

    readme_path = write_readme(commit_hash)
    logger.info("README proof stored at %s", readme_path)

    bundle_artifacts([
        commit_path,
        settings.proof_sig_path,
        settings.proof_sig_enc_path,
        readme_path,
    ])
    logger.info("Proof bundle archived at %s", settings.proof_tar_path)


if __name__ == "__main__":
    main()
