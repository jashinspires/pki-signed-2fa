"""Centralized configuration helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Immutable settings loaded from environment variables."""

    student_id: str = os.getenv("STUDENT_ID", "23A91A0542")
    repo_url: str = os.getenv(
        "REPO_URL", "https://github.com/jashinspires/pki-signed-2fa"
    )
    seed_endpoint: str = os.getenv(
        "SEED_ENDPOINT",
        "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/",
    )
    encrypted_seed_path: Path = Path(
        os.getenv("ENCRYPTED_SEED_PATH", "/data/encrypted_seed.txt")
    )
    seed_path: Path = Path(os.getenv("SEED_PATH", "/data/seed.txt"))
    proof_sig_path: Path = Path(os.getenv("PROOF_SIG_PATH", "/data/proof.sig"))
    proof_sig_enc_path: Path = Path(
        os.getenv("PROOF_SIG_ENC_PATH", "/data/proof.sig.enc")
    )
    proof_tar_path: Path = Path(os.getenv("PROOF_TAR_PATH", "/data/proof.tar.gz"))
    key_dir: Path = Path(os.getenv("KEY_DIR", "/data/keys"))
    cron_log_path: Path = Path(os.getenv("CRON_LOG", "/data/cron.log"))
    instructor_public_key_path: Path = Path(
        os.getenv("INSTRUCTOR_PUB_PATH", "/data/instructor_public.pem")
    )
    student_private_key_name: str = os.getenv(
        "STUDENT_PRIVATE_KEY", "student_private.pem"
    )
    student_public_key_name: str = os.getenv(
        "STUDENT_PUBLIC_KEY", "student_public.pem"
    )
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    def private_key_path(self) -> Path:
        return self.key_dir / self.student_private_key_name

    def public_key_path(self) -> Path:
        return self.key_dir / self.student_public_key_name


def ensure_parent(path: Path) -> None:
    """Ensure the directory for *path* exists."""

    path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
