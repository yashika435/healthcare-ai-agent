# agent/followup_engine.py

from datetime import datetime, timedelta

def estimate_risk_from_symptoms(extracted):
    """
    Rough risk estimate using symptoms only.
    This is separate from vitals-based risk.
    """
    high_flags = ["chest pain", "breathlessness", "high bp"]
    moderate_flags = ["fever", "vomiting", "diarrhea", "low bp", "dizziness"]

    if any(s in extracted for s in high_flags):
        return "High"
    if any(s in extracted for s in moderate_flags):
        return "Moderate"
    return "Low"


def get_followup_plan(symptom_risk):
    """
    Returns (followup_date_str, message)
    """
    today = datetime.now()

    if symptom_risk == "High":
        followup_date = today + timedelta(days=1)
        msg = "Follow-up strongly recommended within 24 hours."
    elif symptom_risk == "Moderate":
        followup_date = today + timedelta(days=3)
        msg = "Follow-up suggested in 2–3 days if symptoms persist."
    else:
        followup_date = today + timedelta(days=7)
        msg = "Routine follow-up after a week is sufficient if no worsening."

    return followup_date.strftime("%Y-%m-%d"), msg
