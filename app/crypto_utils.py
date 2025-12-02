"""Cryptography helper utilities."""
from __future__ import annotations

import base64
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

LOGGER = logging.getLogger(__name__)


def generate_rsa_keypair(bits: int = 4096) -> rsa.RSAPrivateKey:
    """Return a freshly generated private key."""

    return rsa.generate_private_key(public_exponent=65537, key_size=bits)


def write_private_key(key: rsa.RSAPrivateKey, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pem = key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption(),
    )
    path.write_bytes(pem)


def write_public_key(key: rsa.RSAPublicKey, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pem = key.public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)
    path.write_bytes(pem)


def rsa_oaep_decrypt(private_pem_path: Path, ciphertext_b64: str) -> bytes:
    """Decrypt *ciphertext_b64* using RSA/OAEP-SHA256."""

    private_key = serialization.load_pem_private_key(
        private_pem_path.read_bytes(), password=None
    )
    ciphertext = base64.b64decode(ciphertext_b64)
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def rsa_pss_sign(private_pem_path: Path, message: bytes) -> bytes:
    """Sign *message* with RSA-PSS/SHA-256 using maximum salt length."""

    private_key = serialization.load_pem_private_key(
        private_pem_path.read_bytes(), password=None
    )
    signature = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return signature


def rsa_encrypt_with_public(public_pem_path: Path, plaintext: bytes) -> str:
    """Encrypt *plaintext* with RSA/OAEP-SHA256 and return Base64 string."""

    public_key = serialization.load_pem_public_key(public_pem_path.read_bytes())
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(ciphertext).decode("ascii")


def validate_hex_seed(seed: str) -> str:
    """Validate the decrypted seed is a 64-character lowercase hex string."""

    normalized = seed.strip()
    if len(normalized) != 64:
        raise ValueError("Seed must be 64 hexadecimal characters long")
    try:
        int(normalized, 16)
    except ValueError as exc:  # pragma: no cover - guardrail
        raise ValueError("Seed must contain only hexadecimal characters") from exc
    return normalized.lower()


def hex_to_base32(hexstr: str) -> str:
    """Convert a hex string to a base32 string suitable for TOTP."""

    raw = bytes.fromhex(hexstr)
    return base64.b32encode(raw).decode("ascii")


def generate_totp(seed_hex: str, for_time: Optional[int] = None) -> tuple[str, int]:
    """Return the TOTP code and seconds remaining in the 30s window."""

    seed_hex = validate_hex_seed(seed_hex)
    base32_seed = hex_to_base32(seed_hex)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30, digest="sha1")
    code = totp.at(for_time) if for_time else totp.now()
    period = totp.interval
    now = int(for_time or datetime.now(tz=timezone.utc).timestamp())
    remaining = period - (now % period)
    if remaining == period:
        remaining = 0
    return code, remaining


def verify_totp(seed_hex: str, code: str, valid_window: int = 1) -> bool:
    seed_hex = validate_hex_seed(seed_hex)
    base32_seed = hex_to_base32(seed_hex)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30, digest="sha1")
    return totp.verify(code, valid_window=valid_window)
