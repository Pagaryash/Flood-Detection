# sms_alert.py
import json
import os
import requests
from datetime import datetime

CONFIG_PATH = "config/sms_config.json"
LOG_FILE = "data/sms_log.txt"


def _ensure_dirs():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def _digits_only(phone: str) -> str:
    return "".join(c for c in (phone or "") if c.isdigit())


def send_sms_alert(message: str, phone: str):
    """
    Sends SMS using Fast2SMS (API).
    Logs all attempts to data/sms_log.txt (auto-created).
    """
    _ensure_dirs()

    phone = _digits_only(phone)
    if not phone:
        print("❌ SMS phone missing/invalid")
        return False

    with open(CONFIG_PATH) as f:
        cfg = json.load(f)

    api_key = (((cfg.get("fast2sms") or {}).get("apiKey")) or "").strip()
    if not api_key:
        print("❌ Missing fast2sms.apiKey in config/sms_config.json")
        return False

    # Fast2SMS API endpoint (works for API sending)
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "q",
        "message": message,
        "numbers": phone
    }

    headers = {
        "authorization": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }

    try:
        r = requests.post(url, data=payload, headers=headers, timeout=25)
        ok = 200 <= r.status_code < 300

        print("📨 FAST2SMS STATUS:", r.status_code)
        try:
            resp_json = r.json()
            print("📨 FAST2SMS RESPONSE:", resp_json)
        except Exception:
            resp_json = None
            print("📨 FAST2SMS TEXT:", r.text[:500])

        # Log
        log_line = f"[{datetime.now()}] FAST2SMS({r.status_code}) → {phone}: {message}\n"
        with open(LOG_FILE, "a") as lf:
            lf.write(log_line)

        return ok
    except Exception as e:
        print("❌ Fast2SMS error:", e)
        log_line = f"[{datetime.now()}] FAST2SMS(ERROR) → {phone}: {message} | err={repr(e)}\n"
        with open(LOG_FILE, "a") as lf:
            lf.write(log_line)
        return False
