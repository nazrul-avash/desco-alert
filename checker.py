import requests
import urllib3
from datetime import datetime, date

# Suppress the insecure request warnings caused by disabling SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://prepaid.desco.org.bd/api"

# Emulate a real desktop browser request signature
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Origin": "https://prepaid.desco.org.bd",
    "Referer": "https://prepaid.desco.org.bd/"
}

def _get(path: str, params: dict) -> dict | None:
    """Tries unified first, then tkdes. Gracefully bypasses SSL quirks."""
    for meter_type in ["unified", "tkdes"]:
        url = f"{BASE_URL}/{meter_type}/{path}"
        try:
            # Added verify=False to bypass utility certificate validation errors
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15, verify=False)
            
            if resp.status_code == 200:
                body = resp.json()
                # Flexibly grab the data payload directly if it exists
                if "data" in body and body["data"]:
                    return body["data"]
                    
        except Exception as e:
            print(f"[WARN] {meter_type} attempt failed on endpoint {path}: {e}")
            
    return None


def get_balance(account_no: str) -> dict | None:
    """Fetches real-time meter balance array structures."""
    return _get("customer/getBalance", {"accountNo": account_no})


def get_monthly_consumption(account_no: str) -> dict | None:
    """Returns this month's or the previous month's usage summary."""
    today = date.today()
    month_str = today.strftime("%Y-%m")
    
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

    records = data if isinstance(data, list) else [data]
    records.sort(key=lambda r: r.get("month", ""), reverse=True)
    return records[0] if records else None


def build_report(account_no: str, balance_threshold: float) -> dict:
    """Compiles the metrics together into a structured notification report."""
    balance_data = get_balance(account_no)

    if not balance_data:
        return {
            "error": "Unable to extract meter data payload. Your account number might be invalid for both endpoints, or GitHub's server region is currently geo-blocked by DESCO's hosting firewall."
        }

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