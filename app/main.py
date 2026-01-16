import base64
import os
import time
from pathlib import Path

import pyotp
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.crypto_utils import decrypt_seed, load_private_key, validate_hex_seed


app = FastAPI()


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyCodeRequest(BaseModel):
    code: str | None = None


def seed_path() -> Path:
    return Path(os.getenv("SEED_PATH", "/data/seed.txt"))


def private_key_path() -> Path:
    return Path(os.getenv("PRIVATE_KEY_PATH", "student_private.pem"))


def read_seed() -> str:
    path = seed_path()
    if not path.exists():
        raise FileNotFoundError("Seed not decrypted yet")
    hex_seed = path.read_text(encoding="utf-8").strip()
    validate_hex_seed(hex_seed)
    return hex_seed


def hex_seed_to_base32(hex_seed: str) -> str:
    validate_hex_seed(hex_seed)
    return base64.b32encode(bytes.fromhex(hex_seed)).decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    base32_seed = hex_seed_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    base32_seed = hex_seed_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)


@app.get("/health")
def health():
    return {"status": "ok"}


def error_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: DecryptSeedRequest):
    try:
        private_key = load_private_key(private_key_path())
        hex_seed = decrypt_seed(payload.encrypted_seed, private_key)
        path = seed_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(hex_seed, encoding="utf-8")
    except Exception:
        return error_response("Decryption failed", 500)

    return {"status": "ok"}


@app.get("/generate-2fa")
def generate_2fa():
    try:
        hex_seed = read_seed()
        code = generate_totp_code(hex_seed)
        now = int(time.time())
        valid_for = (30 - (now % 30)) % 30
        return {"code": code, "valid_for": valid_for}
    except Exception:
        return error_response("Seed not decrypted yet", 500)


@app.post("/verify-2fa")
def verify_2fa(payload: VerifyCodeRequest):
    if not payload.code:
        return error_response("Missing code", 400)

    try:
        hex_seed = read_seed()
        is_valid = verify_totp_code(hex_seed, payload.code, valid_window=1)
        return {"valid": bool(is_valid)}
    except Exception:
        return error_response("Seed not decrypted yet", 500)
