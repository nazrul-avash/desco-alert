import requests

TELEGRAM_API_URL = "https://api.telegram.org"

def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    """Send a message via Telegram Bot API."""
    url = f"{TELEGRAM_API_URL}/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"  # This allows your *bold* text to render beautifully!
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        success = resp.status_code == 200
        if not success:
            print(f"[ERROR] Telegram returned {resp.status_code}: {resp.text}")
        return success
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message to {chat_id}: {e}")
        return False

def notify_all(token: str, recipients: list[dict], message: str):
    """
    recipients: list of {"chat_id": "987654321", "name": "Me"}
    """
    for r in recipients:
        name = r.get("name", r["chat_id"])
        ok = send_telegram_message(token, r["chat_id"], message)
        status = "✅ Sent" if ok else "❌ Failed"
        print(f"  {status} → {name} ({r['chat_id']})")