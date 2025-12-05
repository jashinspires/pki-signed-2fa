# 🔥 PKI-based 2FA Microservice: The Report

It is **2025**, and your password has definitely been leaked on the dark web.

Welcome to the **PKI-based 2FA Microservice** — a project that proves I understand encryption just enough to be dangerous. While other developers are hardcoding secrets in `.env` files, I decided to suffer through implementing a full Public Key Infrastructure using RSA key pairs, TOTP generation, and Docker containers that actually talk to each other.

This is the story of how I stopped worrying and learned to love the **4096-bit Key**.

## 🧠 The "Brain Expansion" (What I Learned)

This project forced me to understand how the internet actually stays secure. The main concepts I had to download into my smooth brain were:

1.  **Public Key Infrastructure (PKI)**
    Using RSA key pairs where the **Private Key** is for my eyes only (decrypting), and the **Public Key** is for the world (encrypting). I generated a **4096-bit** key pair because 2048-bit is for casuals.

2.  **TOTP (Time-based One-Time Passwords)**
    Those annoying 6-digit codes that change every 30 seconds. The "fun" part was realizing you have to convert the Hex seed to Base32 before generating the code, or else the math doesn't math.

3.  **Docker Containerization**
    Running a FastAPI server AND a Cron job in the same container using `supervisord` (or entrypoint scripts). It uses volumes to persist data so my keys don't vanish when the container crashes.

## ⚙️ The Protocol (How It Works)

The flow is pretty straightforward, assuming you enjoy asymmetric cryptography:

1.  **Generate Keys:** I create a massive RSA 4096-bit key pair (`student_private.pem`, `student_public.pem`).
2.  **The Exchange:** I yeet my Public Key to the Instructor API → It sends back an **Encrypted Seed**.
3.  **The Decryption:** I use my Private Key (RSA/OAEP with SHA-256) to decrypt that seed.
4.  **The Generation:** That decrypted seed is used to spawn TOTP codes.
5.  **The Log:** A cron job wakes up every minute to log the code, proving I am always watching.

## 📂 Project Structure (The Spaghetti)

```text
├── app/
│   ├── main.py          # FastAPI endpoints (The Brain)
│   ├── crypto_utils.py  # The Math (RSA decryption, TOTP logic)
│   └── config.py        # Environment configs
├── scripts/
│   ├── generate_keys.py # Creates the 4096-bit monsters
│   ├── request_seed.py  # Talks to the Instructor API
│   └── log_2fa_cron.py  # The script the cron job runs
├── cron/
│   └── 2fa-cron         # Cron schedule (Every. Single. Minute.)
├── data/
│   ├── keys/            # Where the secrets live (GitIgnored, hopefully)
│   └── instructor_public.pem
├── Dockerfile           # The recipe
├── docker-compose.yml   # The orchestration
└── entrypoint.sh        # Starts Cron + Uvicorn together


## 🚀 How to Deploy This Beast

**Step 1: Generate your Keys**
*The "I have secrets" phase.*

```bash
python scripts/generate_keys.py
```

This spawns `student_private.pem` and `student_public.pem` in `data/keys/`. Don't leak these.

**Step 2: Get the Encrypted Seed**
*The Handshake.*

```bash
python scripts/request_seed.py
```

Sends your public key to the API. Returns a blob of encrypted gibberish (the seed).

**Step 3: Dockerize It**
*Because it works on my machine.*

```bash
docker compose up --build -d
```

**Step 4: Decrypt the Seed**
*The moment of truth.*

```bash
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d '{"encrypted_seed": "<your-encrypted-seed>"}'
```

## 🔌 The Interface (API Endpoints)

| Endpoint | Method | What it does |
|----------|--------|--------------|
| `/health` | GET | Returns `{"status": "ok"}` (Am I alive?) |
| `/decrypt-seed` | POST | Takes the blob, decrypts it, saves it. |
| `/generate-2fa` | GET | Returns the current code + validity window. |
| `/verify-2fa` | POST | Checks if your code is legit or if you're a hacker. |

## 🧪 Sanity Checks (Testing)

Run these commands to verify the system isn't hallucinating.

```bash
# Health Check
curl http://localhost:8080/health

# Generate a Code (Look for the 6 digits)
curl http://localhost:8080/generate-2fa

# Verify a Code
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

## 🕒 The Cron Job (The Stalker)

The container runs a background task every 60 seconds that:

1.  Reads the seed from `/data/seed.txt`.
2.  Generates the TOTP.
3.  Logs it to `/cron/last_code.txt` like a diary entry: `YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX`.

**Spy on the logs:**

```bash
docker exec pki-2fa-web cat /cron/last_code.txt
```

## 🔐 Generating Commit Proof

After you push your final commit and realize you forgot to comment your code:

```bash
python scripts/generate_proof.py
```

This signs your commit hash with **RSA-PSS** and encrypts it with the instructor's key. It’s basically a digital wax seal.

-----

**This has been the PKI-2FA Microservice.**
If you survived reading this without your RSA keys getting corrupted, congratulations.

Thanks for reading, and **I will see you in the next one.**

```
