#!/usr/bin/env python3
import argparse
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keypair(output_dir: Path, force: bool) -> None:
    private_path = output_dir / "student_private.pem"
    public_path = output_dir / "student_public.pem"

    if not force and (private_path.exists() or public_path.exists()):
        raise SystemExit("Key files already exist. Use --force to overwrite.")

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    print(f"Wrote {private_path}")
    print(f"Wrote {public_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RSA 4096-bit keypair")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    generate_keypair(Path(args.output_dir), args.force)
