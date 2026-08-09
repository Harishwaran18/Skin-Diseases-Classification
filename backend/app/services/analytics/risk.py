"""Risk level engine: Green / Yellow / Red (spec Section 23).

Cautious, templated messaging. Never asserts diagnosis. Includes an
emergency disclaimer when serious symptoms are reported.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.symptom import Symptom
from app.models.user import User
from app.services.analytics.trend import trend_summary

EMERGENCY_DISCLAIMER = (
    "If you experience severe symptoms such as difficulty breathing, "
    "swelling of the face/throat, spreading redness with fever, or any "
    "sign of a serious systemic reaction, seek emergency medical care "
    "immediately."
)


def compute_risk(db: Session, user: User, window_days: int = 30) -> dict:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=window_days)
    syms = list(
        db.scalars(
            select(Symptom)
            .where(Symptom.user_id == user.id, Symptom.recorded_at >= start)
            .order_by(Symptom.recorded_at.asc())
        )
    )
    if not syms:
        return {
            "level": "green",
            "message": "No symptom data in the last 30 days. Start logging to see your trend.",
            "emergency_disclaimer": EMERGENCY_DISCLAIMER,
        }
    trend = trend_summary(db, user, window_days)
    recent = syms[-7:]
    recent_max = max(
        max(getattr(s, d) for d in ["itching", "redness", "dryness", "pain", "swelling", "irritation", "burning", "scaling"])
        for s in recent
    )
    severe_count = sum(
        1 for s in syms
        if any(getattr(s, d) >= 4 for d in ["pain", "swelling", "burning"])
    )
    worsening = trend["direction"] == "worsening"

    if trend["current"] is not None and trend["current"] >= 3.5 and worsening:
        level = "red"
        message = (
            "Your symptom scores have risen sharply recently. This is a "
            "screening alert, not a diagnosis. Please consider consulting a "
            "healthcare professional promptly."
        )
    elif severe_count >= 3 or (recent_max >= 4 and worsening):
        level = "red"
        message = (
            "Repeated severe symptom readings were logged. Please consider "
            "consulting a healthcare professional. This is a screening "
            "alert, not a diagnosis."
        )
    elif worsening or severe_count >= 1 or recent_max >= 4:
        level = "yellow"
        message = (
            "Some increased or repeated symptom readings were observed. "
            "Monitor closely and consider discussing with a healthcare "
            "professional if it continues."
        )
    else:
        level = "green"
        message = (
            "Your symptoms appear stable or improving. Continue logging to "
            "keep track. This is not a diagnosis."
        )
    return {
        "level": level,
        "message": message,
        "emergency_disclaimer": EMERGENCY_DISCLAIMER,
        "trend": trend,
    }
