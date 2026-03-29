# alert_manager.py
# Sends the ONE-TIME SMS advisory (once per run per phone number)
from sms_alert import send_sms_alert

# ✅ In-memory tracker: resets automatically when you stop & rerun the program
_SENT_ONE_TIME_SMS = set()


def _digits_only(phone: str) -> str:
    return "".join(c for c in (phone or "") if c.isdigit())


def build_one_time_sms() -> str:
    """
    Short, single-SMS friendly message.
    (Keep it compact so it delivers fully.)
    """
    return (
        "ONE-TIME SMS: You won't receive this again.\n"
        "If WhatsApp breaks, go to nearest safe shelter.\n"
        "Shelters: Wadala-Vidyalankar College; Dadar-BMC School; "
        "Colaba-BMC Hall; Andheri-Civic Center; Thane-TMC Shelter; Navi Mumbai-NMMC Hall.\n"
        "Tips: Don't panic. Avoid floodwater/underpasses. Drink boiled water. "
        "If fever/diarrhea/cuts: call 108."
    )


def send_one_time_sms_if_needed(phone: str) -> bool:
    """
    Sends exactly ONE SMS per run per phone number.
    Returns True if sent now, False if already sent earlier in this run.
    """
    phone = _digits_only(phone)
    if not phone:
        return False

    if phone in _SENT_ONE_TIME_SMS:
        return False

    msg = build_one_time_sms()
    ok = send_sms_alert(msg, phone)

    # Mark as sent only if API call succeeded
    if ok:
        _SENT_ONE_TIME_SMS.add(phone)

    return ok
