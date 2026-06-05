# ⚡ DESCO Prepaid Meter — WhatsApp Alert System

Get WhatsApp notifications when your DESCO prepaid balance is running low, plus a monthly consumption summary. Runs free on GitHub Actions every hour.

---

## How It Works

```
Every hour (GitHub Actions)
    → Hits DESCO API → reads balance + monthly consumption
    → Balance below threshold? → WhatsApp alert via Callmebot 🔔
    → Balance fine? → Silent (no spam)
```

---

## Setup Guide (15 minutes)

### Step 1 — Activate Callmebot for each recipient

Every person who wants alerts does this **once**:

1. Save `+34 644 59 87 87` in your phone contacts as **"Callmebot"**
2. Send this exact message to that number on WhatsApp:
   ```
   I allow callmebot to send me messages
   ```
3. You'll receive a reply with your personal `apikey` (a number like `1234567`)
4. Note down your phone number (with country code, e.g. `+8801XXXXXXXXX`) and apikey

---

### Step 2 — Create a GitHub repo

1. Go to [github.com](https://github.com) → **New repository**
2. Name it `desco-alert` (or anything)
3. Set it to **Private** (recommended — your account number is sensitive)
4. Upload all files from this project into the repo

---

### Step 3 — Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 3 secrets:

| Secret Name | Value | Example |
|---|---|---|
| `DESCO_ACCOUNT_NO` | Your DESCO account number from your bill | `987654321` |
| `BALANCE_THRESHOLD` | Alert when balance drops below this (in TK) | `150` |
| `WHATSAPP_RECIPIENTS` | JSON array (see format below) | see below |

**Format for `WHATSAPP_RECIPIENTS`:**
```json
[
  {"phone": "+8801XXXXXXXXX", "apikey": "111111", "name": "Me"},
  {"phone": "+8801YYYYYYYYY", "apikey": "222222", "name": "Mom"}
]
```
> ⚠️ Must be valid JSON, all on one line when pasting into the secret field.

---

### Step 4 — Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow will now run automatically every hour

---

### Step 5 — Test it manually

1. Go to **Actions** → **DESCO Balance Alert** → **Run workflow**
2. Set "Send status even if balance is OK?" to `true`
3. Click **Run workflow**
4. Check your WhatsApp — you should get a message! ✅

---

## Files

```
desco-alert/
├── main.py              # Entrypoint — ties everything together
├── checker.py           # Hits DESCO API, parses balance + consumption
├── notifier.py          # Sends WhatsApp messages via Callmebot
├── requirements.txt     # Python dependencies (just requests)
└── .github/
    └── workflows/
        └── schedule.yml # GitHub Actions cron config
```

---

## Customization

| Want to change | Where |
|---|---|
| Check frequency | `schedule.yml` → cron expression |
| Alert threshold | `BALANCE_THRESHOLD` secret |
| Add/remove recipients | `WHATSAPP_RECIPIENTS` secret |
| Always get hourly updates | Set `ALWAYS_NOTIFY=true` in workflow env |

**Cron cheatsheet:**
```
"0 * * * *"    → every hour
"0 */2 * * *"  → every 2 hours
"0 */6 * * *"  → every 6 hours
"0 8,20 * * *" → twice a day at 8am and 8pm UTC (2pm and 2am BD time)
```

---

## Sample WhatsApp Alert

```
⚡ DESCO LOW BALANCE ALERT ⚡

🔴 Balance: 87.50 TK (below 150 TK threshold)

📅 Month: 2026-06
💡 Consumed: 142.30 kWh (1820.49 TK)

🕐 Last reading: 2026-06-05 00:00:00

👉 Please recharge soon!
```

---

## Troubleshooting

**Got `code: 16001` / account not found?**
→ Try both `unified` and `tkdes` paths. The checker does this automatically.

**Callmebot not sending?**
→ Make sure the recipient completed the activation step (sent the opt-in message).

**GitHub Actions not running?**
→ GitHub may pause scheduled workflows on repos with no recent commits. Push any small change to re-activate.

**Balance shows 0 or wrong data?**
→ DESCO's API can be slow to update. `readingTime` shows when the meter was last read.
