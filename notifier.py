import requests
from urllib.parse import quote


CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"


def send_whatsapp(phone: str, apikey: str, message: str) -> bool:
    """Send a WhatsApp message via Callmebot. Returns True on success."""
    try:
        resp = requests.get(
            CALLMEBOT_URL,
            params={
                "phone": phone,
                "text": message,
                "apikey": apikey,
            },
            timeout=15,
        )
        success = resp.status_code == 200
        if not success:
            print(f"[ERROR] Callmebot returned {resp.status_code}: {resp.text}")
        return success
    except Exception as e:
        print(f"[ERROR] Failed to send WhatsApp to {phone}: {e}")
        return False


def notify_all(recipients: list[dict], message: str):
    """
    recipients: list of {"phone": "+880...", "apikey": "12345", "name": "You"}
    """
    for r in recipients:
        name = r.get("name", r["phone"])
        ok = send_whatsapp(r["phone"], r["apikey"], message)
        status = "✅ Sent" if ok else "❌ Failed"
        print(f"  {status} → {name} ({r['phone']})")
