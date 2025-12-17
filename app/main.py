"""FastAPI application exposing the PKI-backed 2FA microservice."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import ensure_parent, settings
from app.crypto_utils import (
    generate_totp,
    rsa_oaep_decrypt,
    validate_hex_seed,
    verify_totp,
)
from app.logger import get_logger

LOGGER = get_logger(__name__)
app = FastAPI(title="PKI 2FA Microservice", version="1.0.0")


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str | None = None


class VerifyRequest(BaseModel):
    code: str | None = None
    totp: str | None = None


class VerifyAliasRequest(BaseModel):
    totp: str


def _read_seed() -> str:
    if not settings.seed_path.exists():
        LOGGER.error("Seed file %s is missing", settings.seed_path)
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    seed = settings.seed_path.read_text(encoding="utf-8").strip()
    try:
        return validate_hex_seed(seed)
    except ValueError as exc:
        LOGGER.exception("Seed validation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _write_seed(seed: str) -> None:
    ensure_parent(settings.seed_path)
    settings.seed_path.write_text(seed, encoding="utf-8")


def _append_log(message: str) -> None:
    ensure_parent(settings.cron_log_path)
    with settings.cron_log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"{message}\n")


def _build_totp_payload() -> dict[str, int | str]:
    seed = _read_seed()
    code, remaining = generate_totp(seed)
    LOGGER.info("Generated TOTP code with %s seconds remaining", remaining)
    return {
        "code": code,
        "totp": code,
        "valid_for": remaining,
        "expires_in": remaining,
    }


def _verify_code(code: str) -> bool:
    seed = _read_seed()
    result = verify_totp(seed, code)
    LOGGER.info("Verification attempt %s", "passed" if result else "failed")
    _append_log(f"verify {code} => {result}")
    return result


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/decrypt-seed")
async def decrypt_seed(payload: DecryptSeedRequest | None = None) -> dict[str, str]:
    try:
        encrypted_seed = (payload.encrypted_seed if payload else None) or ""
        if not encrypted_seed:
            if not settings.encrypted_seed_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail="Missing encrypted seed (provide in body or store in encrypted_seed.txt)",
                )
            encrypted_seed = settings.encrypted_seed_path.read_text(
                encoding="utf-8"
            ).strip()

        plaintext = rsa_oaep_decrypt(
            settings.private_key_path(), encrypted_seed
        ).decode("utf-8")
        seed = validate_hex_seed(plaintext)
        _write_seed(seed)
        LOGGER.info("Seed decrypted and stored at %s", settings.seed_path)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - guard for validation errors
        LOGGER.exception("Seed processing failed")
        raise HTTPException(status_code=500, detail="Decryption failed") from exc

    return {"status": "ok"}


@app.get("/generate-2fa")
async def generate_2fa() -> dict[str, int | str]:
    return _build_totp_payload()


@app.get("/generate-totp")
async def generate_totp_alias() -> dict[str, int | str]:
    return _build_totp_payload()


@app.post("/verify-2fa")
async def verify_2fa(payload: VerifyRequest) -> dict[str, bool]:
    code = (payload.code or payload.totp or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    result = _verify_code(code)
    return {"valid": result, "verified": result}


@app.post("/run-totp")
async def run_totp() -> dict[str, str | int]:
    return _build_totp_payload()


@app.post("/verify")
async def verify_alias(payload: VerifyAliasRequest) -> dict[str, bool]:
    return {"verified": _verify_code(payload.totp)}
