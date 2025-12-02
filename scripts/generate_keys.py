"""Generate the student RSA 4096-bit key pair."""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import ensure_parent, settings
from app.crypto_utils import generate_rsa_keypair, write_private_key, write_public_key
from app.logger import configure_logging


def set_permissions(path: Path) -> None:
    try:
        os.chmod(path, 0o600)
    except PermissionError:  # pragma: no cover - Windows fallback
        logging.warning("Unable to set permissions on %s", path)


def main() -> None:
    configure_logging()
    logger = logging.getLogger("generate_keys")

    ensure_parent(settings.key_dir / "placeholder")
    private_path = settings.private_key_path()
    public_path = settings.public_key_path()

    if private_path.exists() or public_path.exists():
        logger.info("Existing key material detected; aborting to avoid overwrite")
        return

    logger.info("Generating 4096-bit RSA key pair")
    private_key = generate_rsa_keypair(bits=4096)
    write_private_key(private_key, private_path)
    write_public_key(private_key.public_key(), public_path)
    set_permissions(private_path)

    logger.info("Private key: %s", private_path)
    logger.info("Public key:  %s", public_path)
    logger.info(
        "IMPORTANT: Commit the public key and follow the PDF guidance for the private key"
    )


if __name__ == "__main__":
    main()
