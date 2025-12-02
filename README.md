# PKI-based 2FA Microservice

## What I Learned

This project helped me understand how real-world authentication systems work. The main concepts I had to grasp were:

1. **Public Key Infrastructure (PKI)** - Using RSA key pairs where the private key decrypts data and the public key encrypts it. I generated a 4096-bit RSA key pair for this.

2. **TOTP (Time-based One-Time Passwords)** - Those 6-digit codes that change every 30 seconds, like Google Authenticator uses. The tricky part was converting the hex seed to base32 before generating codes.

3. **Docker containerization** - Running the API server and cron job together in a container, with volumes to persist data across restarts.

## How It Works

The flow is pretty straightforward once you understand it:

1. Generate RSA 4096-bit key pair (student keys)
2. Send public key to instructor API → get back an encrypted seed
3. Decrypt the seed using private key (RSA/OAEP with SHA-256)
4. Use the decrypted seed to generate TOTP codes
5. A cron job logs the current code every minute

## Project Structure

```
├── app/
│   ├── main.py          # FastAPI endpoints
│   ├── crypto_utils.py  # RSA decryption, TOTP generation
│   └── config.py        # Environment configuration
├── scripts/
│   ├── generate_keys.py # Creates RSA key pair
│   ├── request_seed.py  # Calls instructor API
│   └── log_2fa_cron.py  # Cron script for logging codes
├── cron/
│   └── 2fa-cron         # Cron schedule (runs every minute)
├── data/
│   ├── keys/            # Student private & public keys
│   └── instructor_public.pem
├── Dockerfile
├── docker-compose.yml
└── entrypoint.sh        # Starts cron + uvicorn
```

## Setup Steps

**Step 1: Generate your RSA keys**
```bash
python scripts/generate_keys.py
```
This creates `student_private.pem` and `student_public.pem` in `data/keys/`.

**Step 2: Get the encrypted seed from instructor API**
```bash
python scripts/request_seed.py
```
This sends your public key to the API and saves the encrypted seed.

**Step 3: Build and run the container**
```bash
docker compose up --build -d
```

**Step 4: Decrypt the seed (via API)**
```bash
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d '{"encrypted_seed": "<your-encrypted-seed>"}'
```

## API Endpoints

| Endpoint | Method | What it does |
|----------|--------|--------------|
| `/health` | GET | Returns `{"status": "ok"}` |
| `/decrypt-seed` | POST | Decrypts and stores the seed |
| `/generate-2fa` | GET | Returns current TOTP code + validity |
| `/verify-2fa` | POST | Checks if a code is valid |

## Testing

```bash
# Health check
curl http://localhost:8080/health

# Generate a code
curl http://localhost:8080/generate-2fa

# Verify a code
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

## Cron Job

The container runs a cron job every minute that:
- Reads the seed from `/data/seed.txt`
- Generates the current TOTP code
- Logs it to `/cron/last_code.txt` in format: `YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX`

Check the logs:
```bash
docker exec pki-2fa-web cat /cron/last_code.txt
```

## Generating Commit Proof

After pushing your final commit:
```bash
python scripts/generate_proof.py
```
This signs your commit hash with RSA-PSS and encrypts it with the instructor's public key.
