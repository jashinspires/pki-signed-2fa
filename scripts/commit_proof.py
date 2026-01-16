#!/usr/bin/env python3
import argparse
import base64
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.crypto_utils import encrypt_with_public_key, load_private_key, load_public_key, sign_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate encrypted commit proof")
    parser.add_argument("--commit-hash", required=True, help="40-char git commit hash")
    parser.add_argument("--private-key", default="student_private.pem")
    parser.add_argument("--instructor-public-key", default="instructor_public.pem")
    args = parser.parse_args()

    commit_hash = args.commit_hash.strip()
    if len(commit_hash) != 40:
        raise SystemExit("Commit hash must be 40 hex characters")

    private_key = load_private_key(args.private_key)
    instructor_public = load_public_key(args.instructor_public_key)

    signature = sign_message(commit_hash, private_key)
    encrypted = encrypt_with_public_key(signature, instructor_public)
    b64 = base64.b64encode(encrypted).decode("utf-8")

    print("Commit Hash:", commit_hash)
    print("Encrypted Signature:", b64)


if __name__ == "__main__":
    main()
