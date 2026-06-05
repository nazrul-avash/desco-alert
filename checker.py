import requests
from datetime import datetime, date

BASE_URL = "https://prepaid.desco.org.bd/api"
HEADERS = {"Accept": "application/json, text/plain, */*"}


def _get(path: str, params: dict) -> dict | None:
    """Try unified first, then tkdes. Returns data dict or None."""
    for meter_type in ["unified", "tkdes"]:
        url = f"{BASE_URL}/{meter_type}/{path}"
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            body = resp.json()
            if body.get("code") == 200 and body.get("data"):
                return body["data"]
        except Exception as e:
            print(f"[WARN] {meter_type} request failed: {e}")
    return None


def get_balance(account_no: str) -> dict | None:
    """
    Returns dict with keys:
      balance, currentMonthConsumption, readingTime, meterNo
    or None on failure.
    """
    data = _get("customer/getBalance", {"accountNo": account_no})
    return data


def get_monthly_consumption(account_no: str) -> dict | None:
    """
    Returns this month's consumption record or None.
    """
    today = date.today()
    month_str = today.strftime("%Y-%m")
    # fetch last 2 months just in case current month has no data yet
    prev_month = today.replace(day=1)
    if prev_month.month == 1:
        prev_month = prev_month.replace(year=prev_month.year - 1, month=12)
    else:
        prev_month = prev_month.replace(month=prev_month.month - 1)
    month_from = prev_month.strftime("%Y-%m")

    data = _get(
        "customer/getCustomerMonthlyConsumption",
        {"accountNo": account_no, "monthFrom": month_from, "monthTo": month_str},
    )
    if not data:
        return None

    # data is a list; grab the most recent entry
    records = data if isinstance(data, list) else [data]
    records.sort(key=lambda r: r.get("month", ""), reverse=True)
    return records[0] if records else None


def build_report(account_no: str, balance_threshold: float) -> dict:
    """
    Returns a report dict:
      {
        "balance": float,
        "is_low": bool,
        "month": str,
        "consumed_unit": float,
        "consumed_taka": float,
        "reading_time": str,
        "error": str | None
      }
    """
    balance_data = get_balance(account_no)

    if not balance_data:
        return {"error": "Could not fetch balance from DESCO API. The server may be down."}

    balance = float(balance_data.get("balance", 0))
    reading_time = balance_data.get("readingTime", "N/A")

    monthly = get_monthly_consumption(account_no)
    consumed_unit = float(monthly.get("consumedUnit", 0)) if monthly else 0
    consumed_taka = float(monthly.get("consumedTaka", 0)) if monthly else 0
    month = monthly.get("month", datetime.now().strftime("%Y-%m")) if monthly else "N/A"

    return {
        "balance": balance,
        "is_low": balance <= balance_threshold,
        "month": month,
        "consumed_unit": consumed_unit,
        "consumed_taka": consumed_taka,
        "reading_time": reading_time,
        "error": None,
    }
