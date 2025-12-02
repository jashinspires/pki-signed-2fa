"""Decrypt the instructor-provided seed using the student private key."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import ensure_parent, settings
from app.crypto_utils import rsa_oaep_decrypt, validate_hex_seed
from app.logger import configure_logging


def main() -> None:
    configure_logging()
    logger = logging.getLogger("decrypt_seed")

    if not settings.encrypted_seed_path.exists():
        logger.error("Encrypted seed file not found at %s", settings.encrypted_seed_path)
        sys.exit(1)

    ciphertext = settings.encrypted_seed_path.read_text(encoding="utf-8").strip()
    try:
        plaintext = rsa_oaep_decrypt(settings.private_key_path(), ciphertext)
        seed = validate_hex_seed(plaintext.decode("utf-8"))
    except Exception:  # pragma: no cover - guard for crypto issues
        logger.exception("Failed to decrypt seed")
        sys.exit(1)

    ensure_parent(settings.seed_path)
    settings.seed_path.write_text(seed, encoding="utf-8")
    logger.info("Decrypted seed persisted to %s", settings.seed_path)


if __name__ == "__main__":
    main()
