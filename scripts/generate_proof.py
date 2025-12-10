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

from app.crypto_utils import rsa_encrypt_with_public, rsa_pss_sign
from app.logger import configure_logging


def get_local_paths():
    """Get paths for local (non-Docker) execution."""
    data_dir = ROOT_DIR / "data"
    key_dir = data_dir / "keys"
    return {
        "data_dir": data_dir,
        "key_dir": key_dir,
        "private_key": key_dir / "student_private.pem",
        "instructor_public": data_dir / "instructor_public.pem",
        "proof_sig": data_dir / "proof.sig",
        "proof_sig_enc": data_dir / "proof.sig.enc",
        "proof_tar": data_dir / "proof.tar.gz",
        "commit_hash": data_dir / "commit_hash.txt",
        "readme_proof": data_dir / "README_proof.txt",
    }


def ensure_parent(path: Path) -> None:
    """Ensure the directory for path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def run_git_command(*args: str) -> str:
    result = subprocess.check_output(["git", *args], cwd=ROOT_DIR, text=True).strip()
    return result


def write_commit_hash(path: Path) -> str:
    commit_hash = run_git_command("rev-parse", "--verify", "HEAD")
    ensure_parent(path)
    path.write_text(commit_hash, encoding="utf-8")
    return commit_hash


def write_signature(commit_hash: str, paths: dict) -> None:
    signature = rsa_pss_sign(paths["private_key"], commit_hash.encode("utf-8"))
    ensure_parent(paths["proof_sig"])
    paths["proof_sig"].write_bytes(signature)

    encrypted = rsa_encrypt_with_public(
        paths["instructor_public"],
        signature,
    )
    ensure_parent(paths["proof_sig_enc"])
    paths["proof_sig_enc"].write_text(encrypted, encoding="utf-8")


def write_readme(commit_hash: str, paths: dict) -> Path:
    readme_path = paths["readme_proof"]
    ensure_parent(readme_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    content = (
        "Proof Generation Summary\n"
        f"Timestamp: {timestamp}\n"
        f"Commit Hash: {commit_hash}\n"
        f"Signature: {paths['proof_sig']}\n"
        f"Encrypted Signature: {paths['proof_sig_enc']}\n"
        f"Instructor Public Key: {paths['instructor_public']}\n"
    )
    readme_path.write_text(content, encoding="utf-8")
    return readme_path


def bundle_artifacts(artifact_paths: list[Path], tar_path: Path) -> None:
    ensure_parent(tar_path)
    with tarfile.open(tar_path, "w:gz") as tar:
        for item in artifact_paths:
            if item.exists():
                tar.add(item, arcname=item.name)


def main() -> None:
    configure_logging()
    logger = logging.getLogger("generate_proof")

    paths = get_local_paths()

    if not paths["instructor_public"].exists():
        logger.error(
            "Instructor public key missing at %s",
            paths["instructor_public"],
        )
        raise SystemExit(1)

    if not paths["private_key"].exists():
        logger.error(
            "Student private key missing at %s",
            paths["private_key"],
        )
        raise SystemExit(1)

    commit_hash = write_commit_hash(paths["commit_hash"])
    logger.info("Captured commit hash: %s", commit_hash)

    write_signature(commit_hash, paths)
    logger.info("Signature written to %s", paths["proof_sig"])
    logger.info("Encrypted signature written to %s", paths["proof_sig_enc"])

    readme_path = write_readme(commit_hash, paths)
    logger.info("README proof stored at %s", readme_path)

    bundle_artifacts(
        [
            paths["commit_hash"],
            paths["proof_sig"],
            paths["proof_sig_enc"],
            readme_path,
        ],
        paths["proof_tar"],
    )
    logger.info("Proof bundle archived at %s", paths["proof_tar"])

    # Print submission info
    print("\n" + "=" * 60)
    print("SUBMISSION INFO")
    print("=" * 60)
    print(f"Commit Hash: {commit_hash}")
    print(f"\nEncrypted Commit Signature (single line, copy this):")
    print(paths["proof_sig_enc"].read_text().strip())
    print("=" * 60)


if __name__ == "__main__":
    main()
