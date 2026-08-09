"""Trend analysis: rolling averages + slope (spec Section 18)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.symptom import Symptom
from app.models.user import User

DIMS = [
    "itching", "redness", "dryness", "pain", "swelling",
    "irritation", "burning", "scaling",
]


def _score(sym: Symptom) -> float:
    vals = [getattr(sym, d) for d in DIMS] + [min(sym.lesion_count, 5)]
    return sum(vals) / len(vals)


def trend_summary(db: Session, user: User, window_days: int = 30) -> dict:
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
        return {"direction": "no_data", "slope": 0.0, "current": None, "mean": None}
    by_day: dict[str, list[float]] = {}
    for s in syms:
        by_day.setdefault(s.recorded_at.date().isoformat(), []).append(_score(s))
    days = sorted(by_day.keys())
    avgs = [sum(by_day[d]) / len(by_day[d]) for d in days]
    if len(days) >= 2:
        x = np.arange(len(days))
        slope = float(np.polyfit(x, avgs, 1)[0])
    else:
        slope = 0.0
    current = avgs[-1]
    mean = float(np.mean(avgs))
    if slope < -0.03:
        direction = "improving"
    elif slope > 0.03:
        direction = "worsening"
    else:
        direction = "stable"
    return {
        "direction": direction,
        "slope": round(slope, 4),
        "current": round(current, 2),
        "mean": round(mean, 2),
    }
