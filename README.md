# PKI-Signed 2FA Microservice

> *"The best way to keep a secret is to never have one."* — But when you must, use cryptography.

## So, What's Actually Happening Here?

You know those 6-digit codes your authenticator app generates? The ones that change every 30 seconds? Ever wondered how your phone and the server magically agree on the same number without talking to each other?

That's what this project is about. But let's start with an even more interesting question.

---

## The Real Problem: Sending Secrets Over the Internet

Imagine you want to whisper a secret to someone across a crowded room. Anyone could listen. That's basically the internet.

So how do banks, governments, and yes — your authenticator app — send secrets securely?

### The Padlock Analogy

Here's a brilliant solution humans figured out:

1. I send you an **open padlock** (but I keep the key)
2. You put your secret in a box, snap my padlock shut
3. You send the locked box back to me
4. Only I can open it — because only I have the key

In cryptography, that open padlock is called a **public key**. The key I kept? That's my **private key**. Together, they're called a **key pair**.

This project uses **RSA-4096** — that "4096" means the key is 4096 bits long. To crack it, you'd need to factor a number with over 1,200 digits. Good luck.

### But Wait, There's a Catch

What if someone tampers with the locked box? Or sends a fake one?

That's where **digital signatures** come in. It's like a wax seal on a letter — if anyone messes with it, you'll know. This project uses **RSA-PSS** signatures, which are mathematically provable to be secure.

---

## The Magic of Synchronized Codes

Okay, so we can send secrets securely. But how do two devices generate the same 6-digit code without communicating?

Here's the trick: **they both know the same secret**, and **they both know what time it is**.

### The Recipe

```
Current Time (rounded to 30 seconds) + Shared Secret → Hash Function → 6-digit code
```

A **hash function** is like a meat grinder for data — you put something in, you get a fixed-size output, and you can't reverse it. Same input always gives the same output.

So if my server and your phone both have:
- The same secret (called a **seed**)
- The same time (give or take 30 seconds)

They'll generate the same code. Every. Single. Time.

This is called **TOTP** — Time-based One-Time Password.

---

## What This Project Actually Does

```
┌─────────────────────────────────────────────────────┐
│              Docker Container                        │
│                                                     │
│   ┌─────────────┐         ┌─────────────┐          │
│   │   Web API   │         │  Scheduler  │          │
│   │ (Port 8080) │         │(runs every  │          │
│   │             │         │   minute)   │          │
│   └──────┬──────┘         └──────┬──────┘          │
│          │                       │                  │
│          ▼                       ▼                  │
│   ┌─────────────────────────────────────┐          │
│   │     Shared Secret Storage           │          │
│   │     (survives restarts)             │          │
│   └─────────────────────────────────────┘          │
└─────────────────────────────────────────────────────┘
```

**Docker** is like a shipping container for software — everything the app needs is packed inside, so it runs the same way everywhere.

**The Scheduler (Cron)** is an automatic timer that runs a task every minute, logging the current 2FA code.

---

## The Three Endpoints

Think of these as three buttons you can press:

| Button | What It Does |
|--------|--------------|
| `POST /decrypt-seed` | "Here's an encrypted secret — decrypt it and remember it" |
| `GET /generate-2fa` | "What's the current 6-digit code?" |
| `POST /verify-2fa` | "Is this code valid right now?" |

---

## Try It Yourself

```bash
# Start the container
docker-compose up -d

# Send an encrypted seed to be decrypted
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d '{"encrypted_seed": "YOUR_ENCRYPTED_SEED"}'

# Get the current code
curl http://localhost:8080/generate-2fa
# Returns: {"code": "482916", "valid_for": 23}

# Check if a code is valid
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "482916"}'
# Returns: {"valid": true}
```

---

## The Technical Bits (For the Curious)

### Encryption Settings
- **RSA-4096**: Very large key, very secure
- **OAEP padding**: Adds randomness so the same message encrypts differently each time
- **SHA-256**: A hash function that outputs 256 bits — used in Bitcoin too

### TOTP Settings
- **SHA-1 hash**: Yes, it's older, but it's what authenticator apps expect
- **30-second window**: Codes change every half minute
- **6 digits**: 1 million possibilities, but only valid for 30-90 seconds

---

## Project Structure

```
.
├── app/
│   ├── main.py          # The web server
│   └── crypto_utils.py  # Encryption/decryption functions
├── scripts/
│   ├── generate_keys.py # Creates your key pair
│   ├── request_seed.py  # Gets encrypted seed from API
│   ├── commit_proof.py  # Signs your work cryptographically
│   └── log_2fa_cron.py  # The scheduled task
├── cron/
│   └── 2fa-cron         # Schedule configuration
├── Dockerfile           # Container blueprint
├── docker-compose.yml   # Container settings
└── requirements.txt     # Python libraries needed
```

---

## Things That Surprised Me

1. **Cryptography is unforgiving** — Get one parameter wrong, and it silently fails. No helpful error messages.

2. **Time zones matter** — If your server thinks it's 3 PM and your phone thinks it's 4 PM, the codes won't match.

3. **Line endings break things** — Windows uses `\r\n`, Linux uses `\n`. A single wrong character can break a scheduled task.

4. **The math actually works** — It's wild that two devices can agree on a number without communicating, just by sharing a secret and checking their clocks.

---

## Why Should You Care?

Every time you:
- Log into your bank
- Use Google Authenticator
- See that little padlock in your browser

...this is what's happening under the hood. The same math. The same principles.

Understanding it doesn't just make you a better developer. It makes you appreciate the invisible infrastructure keeping your digital life secure.

---

*"In cryptography, we trust mathematics, not people."*
