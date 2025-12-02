"""Request the encrypted seed from the instructor endpoint."""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import requests
from requests import Response

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import ensure_parent, settings
from app.logger import configure_logging

TIMEOUT_SECONDS = 10
MAX_ATTEMPTS = 2


def load_public_key() -> str:
    path = settings.public_key_path()
    if not path.exists():
        raise FileNotFoundError(f"Public key not found at {path}")
    return path.read_text(encoding="utf-8")


def send_request(payload: dict[str, Any]) -> Response:
    last_exc: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.post(
                settings.seed_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response
        except Exception as exc:  # pragma: no cover - network edge cases
            last_exc = exc
            logging.error("Seed request attempt %s failed: %s", attempt, exc)
            if attempt < MAX_ATTEMPTS:
                time.sleep(2)
    assert last_exc is not None
    raise last_exc


def main() -> None:
    configure_logging()
    logger = logging.getLogger("request_seed")

    public_key = load_public_key()
    payload = {
        "student_id": settings.student_id,
        "github_repo_url": settings.repo_url,
        "public_key": public_key,
    }
    logger.info("Requesting encrypted seed from %s", settings.seed_endpoint)

    response = send_request(payload)
    data = response.json()
    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        logger.error("Encrypted seed missing in response: %s", json.dumps(data))
        sys.exit(1)

    ensure_parent(settings.encrypted_seed_path)
    settings.encrypted_seed_path.write_text(encrypted_seed, encoding="utf-8")
    logger.info(
        "Encrypted seed stored at %s (%s bytes)",
        settings.encrypted_seed_path,
        len(encrypted_seed),
    )


if __name__ == "__main__":
    main()
