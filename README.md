# PKI-Signed 2FA Microservice

> *"The best way to keep a secret is to never have one."* — But when you must, use cryptography.

## What Is This?

This is a containerized microservice that demonstrates how modern authentication systems work under the hood. It combines two powerful security concepts:

1. **Public Key Infrastructure (PKI)** — The same technology that secures your HTTPS connections
2. **Time-based One-Time Passwords (TOTP)** — The 6-digit codes from your authenticator app

This project was built as part of a course assignment to explore enterprise-grade security practices.

---

## The Fascinating Problem

Here's the challenge: How do you transmit a secret (like a 2FA seed) over an untrusted network, ensure only the intended recipient can read it, and then use that secret to generate time-synchronized codes?

The answer involves some beautiful mathematics and clever engineering.

### The RSA Dance

When you want to send someone a secret:
1. They give you their **public key** (like a padlock)
2. You lock your message with their padlock
3. Only their **private key** can unlock it

This project uses RSA-4096 with OAEP padding — the same standard used by banks and governments.

### The TOTP Magic

Your authenticator app and the server never communicate after initial setup. Yet they generate the same 6-digit code. How?

They share a secret seed and use the current time (in 30-second intervals) as input to a one-way function. Same seed + same time = same code. It's like two synchronized clocks that speak in numbers.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Docker Container                    │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  FastAPI    │    │    Cron     │                │
│  │   Server    │    │    Job      │                │
│  │  (Port 8080)│    │  (1 min)    │                │
│  └──────┬──────┘    └──────┬──────┘                │
│         │                  │                        │
│         ▼                  ▼                        │
│  ┌─────────────────────────────────────┐           │
│  │         /data/seed.txt              │           │
│  │      (Persistent Volume)            │           │
│  └─────────────────────────────────────┘           │
└─────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/decrypt-seed` | POST | Decrypt and store the 2FA seed |
| `/generate-2fa` | GET | Generate current TOTP code |
| `/verify-2fa` | POST | Verify a TOTP code (±30s tolerance) |
| `/health` | GET | Health check |

---

## Quick Start

```bash
# Build and run
docker-compose up -d

# Decrypt the seed (replace with your encrypted seed)
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d '{"encrypted_seed": "YOUR_ENCRYPTED_SEED"}'

# Generate a 2FA code
curl http://localhost:8080/generate-2fa

# Verify a code
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

---

## Technical Specifications

### Cryptographic Parameters
- **Key Size**: RSA 4096-bit
- **Encryption**: RSA/OAEP with SHA-256 and MGF1
- **Signatures**: RSA-PSS with SHA-256 (max salt length)
- **TOTP**: SHA-1, 30-second period, 6 digits

### Why These Choices?

- **RSA-4096**: Provides security margin until ~2030+ against classical computers
- **OAEP Padding**: Prevents padding oracle attacks that broke earlier schemes
- **PSS Signatures**: Provably secure in the random oracle model
- **SHA-1 for TOTP**: Standard compatibility (your authenticator app expects this)

---

## Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI application
│   └── crypto_utils.py  # RSA operations
├── scripts/
│   ├── generate_keys.py # Key pair generation
│   ├── request_seed.py  # Instructor API client
│   ├── commit_proof.py  # Signature generation
│   └── log_2fa_cron.py  # Cron job script
├── cron/
│   └── 2fa-cron         # Cron configuration
├── Dockerfile           # Multi-stage build
├── docker-compose.yml   # Container orchestration
└── requirements.txt     # Python dependencies
```

---

## What I Learned

Building this project revealed several insights:

1. **Cryptography is precise** — Wrong padding scheme? Decryption fails silently.
2. **Time synchronization matters** — TOTP codes are useless if clocks drift.
3. **Line endings matter** — CRLF in a cron file breaks Linux.
4. **Docker volumes persist** — But only if you configure them correctly.

---

## Acknowledgments

This project was developed as part of a course assignment. The architecture and requirements were provided by the instructor. The implementation demonstrates practical application of:

- Public Key Infrastructure (PKI)
- TOTP Authentication (RFC 6238)
- Docker containerization
- REST API design

---

## License

This project is for educational purposes as part of coursework.

---

*"In cryptography, we trust mathematics, not people."*
