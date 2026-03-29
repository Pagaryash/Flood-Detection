# whatsapp_alert.py
import json
import os
import requests

GREEN_CONFIG_PATH = "config/greenapi_config.json"


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    with open(path, "r") as f:
        return json.load(f)


green_cfg = load_json(GREEN_CONFIG_PATH)

ID_INSTANCE = (green_cfg.get("idInstance") or "").strip()
API_TOKEN = (green_cfg.get("apiTokenInstance") or "").strip()
TARGET_NUMBER = (green_cfg.get("targetNumber") or "").strip()

if not ID_INSTANCE or not API_TOKEN:
    raise ValueError("greenapi_config.json must include idInstance and apiTokenInstance")


def normalize_phone_digits(phone: str) -> str:
    return "".join(c for c in (phone or "") if c.isdigit())


def send_whatsapp_alert(message: str, phone: str | None = None):
    """Send WhatsApp alert using Green API (separate from bot replies)."""
    phone = normalize_phone_digits(phone or TARGET_NUMBER)
    if not phone:
        raise ValueError("targetNumber missing in config/greenapi_config.json")

    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {"chatId": f"{phone}@c.us", "message": message}

    r = requests.post(url, json=payload, timeout=25)
    print("SEND STATUS:", r.status_code)
    try:
        print("SEND RESPONSE JSON:", r.json())
    except Exception:
        print("SEND RESPONSE TEXT:", r.text[:400])

    return r.ok
