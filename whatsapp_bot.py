# whatsapp_bot.py
# ==========================================
# FLOOD SAFETY BOT (Green API)
# - WhatsApp webhook -> replies (unchanged content)
# - SMS: ONE-TIME advisory per run per phone number
# - Admin dashboard at /admin (simple)
# - Runs on port 5050
# ==========================================

from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os
from collections import deque
from datetime import datetime

from alert_manager import send_one_time_sms_if_needed  # ✅ SMS only once per run

app = Flask(__name__)

# ---------- CONFIG PATHS ----------
GREEN_CONFIG_PATH = "config/greenapi_config.json"


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}")
    with open(path, "r") as f:
        return json.load(f)


# ---------- LOAD CONFIG ----------
green_cfg = load_json(GREEN_CONFIG_PATH)

GREEN_API_INSTANCE_ID = (green_cfg.get("idInstance") or "").strip()
GREEN_API_TOKEN = (green_cfg.get("apiTokenInstance") or "").strip()
TARGET_NUMBER = (green_cfg.get("targetNumber") or "").strip()

if not GREEN_API_INSTANCE_ID or not GREEN_API_TOKEN:
    raise ValueError("greenapi_config.json must include idInstance and apiTokenInstance")


# ---------- HELPERS ----------
def normalize_phone_digits(phone: str) -> str:
    return "".join(c for c in (phone or "") if c.isdigit())


def chat_id_from_phone(phone_digits: str) -> str:
    return f"{normalize_phone_digits(phone_digits)}@c.us"


def greenapi_url(method: str) -> str:
    return f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/{method}/{GREEN_API_TOKEN}"


def send_whatsapp(message: str, phone_digits: str) -> bool:
    phone_digits = normalize_phone_digits(phone_digits)
    if not phone_digits:
        return False

    payload = {"chatId": chat_id_from_phone(phone_digits), "message": message}
    try:
        r = requests.post(greenapi_url("sendMessage"), json=payload, timeout=20)
        print("SEND ->", payload["chatId"], r.status_code)
        return 200 <= r.status_code < 300
    except Exception as e:
        print("Send error:", e)
        return False


def extract_message_and_sender(data: dict):
    sender = (data.get("senderData") or {}).get("chatId") or data.get("chatId")
    msg = (
        (data.get("messageData", {}) or {})
        .get("textMessageData", {})
        .get("textMessage")
    ) or data.get("text")
    return msg, sender


# ---------- FIXED LOCATION ----------
SOURCE_ADDRESS = "2VCC+J6V, College Marg, Wadala(E), Sangam Nagar, Mumbai, Maharashtra 400037"
SOURCE_COORDS = (19.0255, 72.8791)  # Wadala

# ---------- AREAS ----------
AREAS = {
    "dadar": ("Dadar", 19.0190, 72.8479),
    "andheri": ("Andheri", 19.1196, 72.8460),
    "borivali": ("Borivali", 19.2250, 72.8560),
    "bandra": ("Bandra", 19.0600, 72.8361),
    "chembur": ("Chembur", 19.0660, 72.9000),
    "colaba": ("Colaba", 18.9076, 72.8147),
    "wadala": ("Wadala", 19.0255, 72.8791),
    "parel": ("Parel", 18.9986, 72.8375),
    "sion": ("Sion", 19.0430, 72.8640),
    "thane": ("Thane", 19.2183, 72.9781),
    "navi mumbai": ("Navi Mumbai", 19.0330, 73.0297),
}

# ---------- PERSISTENT FLOOD STATUS ----------
STATUS_DIR = "dashboard"
STATUS_FILE = os.path.join(STATUS_DIR, "flood_status.json")
os.makedirs(STATUS_DIR, exist_ok=True)

if os.path.exists(STATUS_FILE):
    try:
        with open(STATUS_FILE, "r") as f:
            FLOOD_STATUS = json.load(f)
    except Exception:
        FLOOD_STATUS = {}
else:
    FLOOD_STATUS = {}

for area in AREAS:
    FLOOD_STATUS.setdefault(area, "No Flood")
FLOOD_STATUS.setdefault("mumbai", "No Flood")

with open(STATUS_FILE, "w") as f:
    json.dump(FLOOD_STATUS, f, indent=2)

STATUS_LOG = deque(maxlen=50)


def log_update(area: str, status: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    STATUS_LOG.append({"area": area, "status": status, "time": now})
    with open(STATUS_FILE, "w") as f:
        json.dump(FLOOD_STATUS, f, indent=2)


# ---------- EMERGENCY SERVICES ----------
SERVICES = {
    "hospital": ("KEM Hospital", "Parel", "3.5 km", "10 min", "022-24107000", "https://maps.app.goo.gl/KEM123"),
    "hospital_sion": ("Lokmanya Tilak Municipal General Hospital (Sion Hospital)",
                      "Sion", "2.8 km", "8 min", "022-24076381", "https://maps.app.goo.gl/SionHospital123"),
    "uhc": ("Wadala UHC", "Near Wadala Bridge", "1.2 km", "5 min", "022-24131212", "https://maps.app.goo.gl/WadalaUHC"),
    "fire": ("Wadala Fire Brigade", "Antop Hill", "2.1 km", "7 min", "101", "https://maps.app.goo.gl/WadalaFire"),
    "police": ("Wadala Police Station", "Near Station", "1.8 km", "6 min", "100", "https://maps.app.goo.gl/WadalaPS"),
}

HELPLINES = {
    "Ambulance": "108",
    "Disaster Management": "1916 / 1070",
    "Police": "100",
    "Fire": "101",
}

NGOS = {
    "Mumbai First": "1800 222 100 – Rescue & relief",
    "Goonj": "SMS 92232 23232 – Material aid",
}

FIRST_AID = {
    "drowning": "• Keep calm, float on back\n• If unconscious: Start CPR\n• Call 108\n• Do NOT give food",
    "injury": "• Apply pressure with clean cloth\n• Elevate limb\n• Do NOT remove objects\n• Call 108",
    "shock": "• Lay flat, raise legs 12 inches\n• Keep warm\n• Do NOT give food/drink\n• Monitor breathing",
    "electrocution": "• DO NOT touch directly\n• Switch off power\n• Use wood to separate\n• Call 108 & 101",
}

SHELTERS = [
    ("Vidyalankar College", "Wadala", "1.0 km", "500 capacity", "Open 24/7"),
    ("Antop Hill School", "Wadala", "1.5 km", "400 capacity", "Medical aid"),
]

SAFETY_CHECKLIST = (
    "FLOOD SAFETY CHECKLIST:\n"
    "Avoid moving water\n"
    "Don’t drive in floods\n"
    "Stay away from electric poles\n"
    "Keep torch, water, meds\n"
    "Charge phone fully\n"
    "Listen to radio"
)

OFFLINE_TIPS = (
    "OFFLINE MODE\n"
    "1. Stay on high ground\n"
    "2. Avoid electric wires\n"
    "3. Drink boiled water only\n"
    "4. Call 108 from any phone"
)


# ---------- TEXT HEATMAP ----------
def get_flood_heatmap():
    lines = [
        "MUMBAI FLOOD HEATMAP\n",
        "Legend: [No Flood]=Safe | [Mild]=Caution | [Severe]=Danger\n",
    ]
    for area in ["colaba", "dadar", "wadala", "andheri", "thane", "navi mumbai"]:
        status = FLOOD_STATUS.get(area, "No Flood")
        icon = "[No Flood]" if "no" in status.lower() else "[Mild Flood]" if "mild" in status.lower() else "[Severe Flood]"
        star = " ← You" if area == "wadala" else ""
        lines.append(f"{area.capitalize():12} {icon}{star}")
    return "\n".join(lines)


def get_flood_message(location):
    status = FLOOD_STATUS.get((location or "").lower(), "No Flood")
    loc_name = (location or "mumbai").capitalize()
    if "no flood" in status.lower():
        return f"{status} in {loc_name}. Roads are clear. Safe to travel."
    if "mild" in status.lower():
        return f"{status} in {loc_name}. Avoid low-lying areas. Use elevated paths."
    if "moderate" in status.lower():
        return f"{status} in {loc_name}. Travel only if necessary. Use trains."
    if "severe" in status.lower():
        return f"{status} in {loc_name}! Stay indoors. Do NOT go out."
    return f"Status: {status} in {loc_name}."


def get_route(dest_key):
    if dest_key not in AREAS:
        return "Where to? Try: *route to dadar*"
    name, lat, lng = AREAS[dest_key]
    dist = round(((SOURCE_COORDS[0] - lat) ** 2 + (SOURCE_COORDS[1] - lng) ** 2) ** 0.5 * 111, 1)
    time = int(dist * 3.8)
    link = f"https://www.google.com/maps/dir/{SOURCE_COORDS[0]},{SOURCE_COORDS[1]}/{lat},{lng}"
    tip = "Use local train" if dest_key in ["dadar", "bandra", "andheri"] else "Avoid underpasses"
    return f"*Route: Wadala → {name}*\nDistance: {dist} km | ETA: {time} min\nMaps: {link}\nTip: {tip}"


def menu_reply():
    return (
        "Try:\n"
        "• flood status (e.g., 'flood in dadar')\n"
        "• route to dadar\n"
        "• help / emergency\n"
        "• first aid: drowning / injury / shock / electric\n"
        "• safety checklist\n"
        "• heatmap\n"
        "• shelter\n"
        "• volunteer\n"
        "• offline"
    )


def detect_intent(msg: str):
    m = (msg or "").lower().strip()
    if any(x in m for x in ["drown", "drowning"]): return "first_aid_drowning"
    if any(x in m for x in ["injury", "injured", "cut", "blood", "bleed"]): return "first_aid_injury"
    if "shock" in m: return "first_aid_shock"
    if any(x in m for x in ["electric", "electrocution", "current", "wire"]): return "first_aid_electrocution"
    if any(x in m for x in ["hi", "hello", "hey"]): return "greeting"
    if any(x in m for x in ["flood", "status"]): return "flood"
    if any(x in m for x in ["route", "reach", "go"]): return "route"
    if any(x in m for x in ["help", "emergency", "ngo"]): return "emergency"
    if any(x in m for x in ["checklist", "safety"]): return "safety"
    if any(x in m for x in ["heatmap", "map"]): return "heatmap"
    if any(x in m for x in ["shelter", "evacuate"]): return "shelter"
    if any(x in m for x in ["offline", "no internet"]): return "offline"
    return "unknown"


# ========== WEBHOOK ==========
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "ignored"})

    msg, sender = extract_message_and_sender(data)
    if not msg or not sender:
        return jsonify({"status": "ignored"})

    print(f"[{datetime.now().strftime('%H:%M')}] {sender}: {msg}")

    phone = sender.split("@")[0]
    intent = detect_intent(msg)
    reply = ""

    # ✅ WhatsApp replies unchanged logic
    if intent == "first_aid_drowning":
        reply = f"*FIRST AID: DROWNING*\n{FIRST_AID['drowning']}"
    elif intent == "first_aid_injury":
        reply = f"*FIRST AID: INJURY*\n{FIRST_AID['injury']}"
    elif intent == "first_aid_shock":
        reply = f"*FIRST AID: SHOCK*\n{FIRST_AID['shock']}"
    elif intent == "first_aid_electrocution":
        reply = f"*FIRST AID: ELECTROCUTION*\n{FIRST_AID['electrocution']}"
    elif intent == "greeting":
        reply = "Hi! I'm your *Flood Safety Assistant*.\n\n" + menu_reply()
    elif intent == "flood":
        loc = "mumbai"
        ml = msg.lower()
        for area in AREAS:
            if area in ml:
                loc = area
                break
        reply = get_flood_message(loc)
    elif intent == "route":
        ml = msg.lower()
        dest = None
        for area in AREAS:
            if area in ml:
                dest = area
                break
        reply = get_route(dest) if dest else "Where to? Try: *route to dadar*"
    elif intent == "emergency":
        reply = "*EMERGENCY HELP*\n\n"
        for _, (name, addr, dist, t, phone_num, maps) in SERVICES.items():
            reply += f"*{name}*\n {addr} | {dist} | {t}\n {phone_num}\n {maps}\n\n"
        reply += "*Helplines*\n"
        for n, p in HELPLINES.items():
            reply += f" {n}: {p}\n"
        reply += "\n*NGO Support*\n"
        for n, i in NGOS.items():
            reply += f" {n}: {i}\n"
        reply += "\n*Need First Aid?* Reply with:\n• drowning\n• injury\n• shock\n• electric"
    elif intent == "safety":
        reply = SAFETY_CHECKLIST
    elif intent == "heatmap":
        reply = get_flood_heatmap()
    elif intent == "shelter":
        reply = "*Shelters*\n• " + "\n• ".join([s[0] + " (" + s[1] + ")" for s in SHELTERS])
    elif intent == "offline":
        reply = OFFLINE_TIPS
    else:
        reply = menu_reply()

    # 1) Send WhatsApp reply (normal)
    send_whatsapp(reply, phone)

    # 2) Send ONE-TIME SMS advisory (only once per run per phone)
    send_one_time_sms_if_needed(phone)

    return jsonify({"status": "success"})


# ---------- SIMPLE ADMIN ----------
@app.route("/admin")
def admin():
    all_areas = sorted(set(AREAS.keys()) | {"mumbai"})
    status_dict = {area: FLOOD_STATUS.get(area, "No Flood") for area in all_areas}
    html = """
    <h3>Flood Bot Admin ✅</h3>
    <h4>Current Flood Status</h4>
    <ul>
      {% for a, s in status_dict.items() %}
        <li><b>{{a}}</b>: {{s}}</li>
      {% endfor %}
    </ul>
    """
    return render_template_string(html, status_dict=status_dict)


@app.route("/")
def home():
    return "<h3>Flood Safety Bot running ✅</h3>"


if __name__ == "__main__":
    print("🚀 Flood Bot running on :5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
