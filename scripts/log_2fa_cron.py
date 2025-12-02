"""Cron entry point that logs the current TOTP code."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import ensure_parent, settings
from app.crypto_utils import generate_totp, validate_hex_seed


def read_seed() -> str:
    if not settings.seed_path.exists():
        raise FileNotFoundError(f"Seed file missing at {settings.seed_path}")
    seed = settings.seed_path.read_text(encoding="utf-8").strip()
    return validate_hex_seed(seed)


def main() -> None:
    seed = read_seed()
    code, _ = generate_totp(seed)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    ensure_parent(settings.cron_log_path)
    with settings.cron_log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} - 2FA Code: {code}\n")

    # Mirror output into /cron/last_code.txt for historical parity
    cron_volume = Path("/cron/last_code.txt")
    cron_volume.parent.mkdir(parents=True, exist_ok=True)
    with cron_volume.open("a", encoding="utf-8") as cron_file:
        cron_file.write(f"{timestamp} - 2FA Code: {code}\n")

    print(f"{timestamp} - 2FA Code: {code}")


if __name__ == "__main__":
    main()