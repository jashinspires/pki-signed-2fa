#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from urllib import request


DEFAULT_API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"


def request_seed(student_id: str, github_repo_url: str, public_key_path: Path, api_url: str) -> str:
    public_key = public_key_path.read_text(encoding="utf-8")
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key,
    }
    data = json.dumps(payload).encode("utf-8")

    req = request.Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
    parsed = json.loads(body)
    if parsed.get("status") != "success" or "encrypted_seed" not in parsed:
        raise SystemExit(f"Unexpected API response: {parsed}")
    return parsed["encrypted_seed"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Request encrypted seed from instructor API")
    parser.add_argument("--student-id", required=True)
    parser.add_argument("--github-repo-url", required=True)
    parser.add_argument(
        "--public-key",
        default="student_public.pem",
        help="Path to student public key PEM",
    )
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--output", default="encrypted_seed.txt")
    args = parser.parse_args()

    encrypted_seed = request_seed(
        args.student_id,
        args.github_repo_url,
        Path(args.public_key),
        args.api_url,
    )
    Path(args.output).write_text(encrypted_seed, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
