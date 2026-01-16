#!/usr/bin/env python3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyotp

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.crypto_utils import validate_hex_seed  # noqa: E402


def seed_path() -> Path:
    return Path("/data/seed.txt")


def hex_seed_to_base32(hex_seed: str) -> str:
    validate_hex_seed(hex_seed)
    return __import__("base64").b32encode(bytes.fromhex(hex_seed)).decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    base32_seed = hex_seed_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()


def main() -> int:
    try:
        hex_seed = seed_path().read_text(encoding="utf-8").strip()
        validate_hex_seed(hex_seed)
        code = generate_totp_code(hex_seed)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - 2FA Code: {code}")
        return 0
    except Exception as exc:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
