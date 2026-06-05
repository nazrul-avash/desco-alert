import os
import json
from checker import build_report
from notifier import notify_all

# ── CONFIG (loaded from environment variables / GitHub Secrets) ───────────────

ACCOUNT_NO = os.environ["DESCO_ACCOUNT_NO"]
BALANCE_THRESHOLD = float(os.environ.get("BALANCE_THRESHOLD", "100"))

# RECIPIENTS: JSON string stored in secret, e.g.:
# [{"phone":"+8801XXXXXXXXX","apikey":"111111","name":"Me"},
#  {"phone":"+8801YYYYYYYYY","apikey":"222222","name":"Mom"}]
RECIPIENTS = json.loads(os.environ["WHATSAPP_RECIPIENTS"])

# Optional: set to "true" to always send a status message (not just on low balance)
ALWAYS_NOTIFY = os.environ.get("ALWAYS_NOTIFY", "false").lower() == "true"

# ─────────────────────────────────────────────────────────────────────────────


def format_low_balance_message(report: dict) -> str:
    return (
        f"⚡ *DESCO LOW BALANCE ALERT* ⚡\n\n"
        f"🔴 Balance: *{report['balance']:.2f} TK* (below {BALANCE_THRESHOLD} TK threshold)\n\n"
        f"📅 Month: {report['month']}\n"
        f"💡 Consumed: {report['consumed_unit']:.2f} kWh ({report['consumed_taka']:.2f} TK)\n\n"
        f"🕐 Last reading: {report['reading_time']}\n\n"
        f"👉 Please recharge soon!"
    )


def format_status_message(report: dict) -> str:
    status = "🟢 OK" if not report["is_low"] else "🔴 LOW"
    return (
        f"⚡ *DESCO Meter Status* ⚡\n\n"
        f"💰 Balance: *{report['balance']:.2f} TK* {status}\n\n"
        f"📅 Month: {report['month']}\n"
        f"💡 Consumed: {report['consumed_unit']:.2f} kWh ({report['consumed_taka']:.2f} TK)\n\n"
        f"🕐 Last reading: {report['reading_time']}"
    )


def format_error_message(error: str) -> str:
    return (
        f"⚡ *DESCO Alert System* ⚡\n\n"
        f"❌ Error fetching meter data:\n{error}\n\n"
        f"Please check the DESCO API manually."
    )


def main():
    print(f"🔍 Checking DESCO meter for account: {ACCOUNT_NO}")
    print(f"📊 Alert threshold: {BALANCE_THRESHOLD} TK")

    report = build_report(ACCOUNT_NO, BALANCE_THRESHOLD)

    if report.get("error"):
        print(f"❌ Error: {report['error']}")
        message = format_error_message(report["error"])
        print("📲 Notifying recipients about error...")
        notify_all(RECIPIENTS, message)
        return

    print(f"💰 Current balance: {report['balance']:.2f} TK")
    print(f"💡 This month consumed: {report['consumed_unit']:.2f} kWh ({report['consumed_taka']:.2f} TK)")
    print(f"🕐 Last reading: {report['reading_time']}")

    if report["is_low"]:
        print(f"🚨 Balance is LOW! Sending alert...")
        message = format_low_balance_message(report)
        notify_all(RECIPIENTS, message)
    elif ALWAYS_NOTIFY:
        print(f"📋 Balance OK. Sending status update (ALWAYS_NOTIFY=true)...")
        message = format_status_message(report)
        notify_all(RECIPIENTS, message)
    else:
        print(f"✅ Balance is fine. No notification needed.")


if __name__ == "__main__":
    main()
