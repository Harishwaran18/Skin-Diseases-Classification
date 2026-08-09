"""Symptom service: logging + trends."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.symptom import Symptom
from app.models.user import User

DIMS = [
    "itching", "redness", "dryness", "pain", "swelling",
    "irritation", "burning", "scaling",
]


def create_symptom(db: Session, user: User, data: dict) -> Symptom:
    s = Symptom(user_id=user.id, **data)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def list_symptoms(
    db: Session,
    user: User,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = 200,
) -> list[Symptom]:
    q = select(Symptom).where(Symptom.user_id == user.id)
    if date_from:
        q = q.where(Symptom.recorded_at >= date_from)
    if date_to:
        q = q.where(Symptom.recorded_at <= date_to)
    q = q.order_by(Symptom.recorded_at.desc()).limit(limit)
    return list(db.scalars(q))


def _score(sym: Symptom) -> float:
    vals = [getattr(sym, d) for d in DIMS] + [min(sym.lesion_count, 5)]
    return sum(vals) / len(vals)


def compute_trend(
    db: Session, user: User, window_days: int = 30
) -> dict:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=window_days)
    syms = list(
        db.scalars(
            select(Symptom)
            .where(Symptom.user_id == user.id, Symptom.recorded_at >= start)
            .order_by(Symptom.recorded_at.asc())
        )
    )
    # group by day
    by_day: dict[str, list[float]] = {}
    for s in syms:
        key = s.recorded_at.date().isoformat()
        by_day.setdefault(key, []).append(_score(s))
    points = []
    for day, scores in sorted(by_day.items()):
        points.append({
            "date": day,
            "avg_score": round(sum(scores) / len(scores), 2),
            "max_score": round(max(scores), 2),
            "count": len(scores),
        })
    if len(points) >= 2:
        first_half = points[: len(points) // 2]
        second_half = points[len(points) // 2 :]
        a = sum(p["avg_score"] for p in first_half) / len(first_half)
        b = sum(p["avg_score"] for p in second_half) / len(second_half)
        if b < a - 0.2:
            direction = "improving"
        elif b > a + 0.2:
            direction = "worsening"
        else:
            direction = "stable"
    elif len(points) == 1:
        direction = "stable"
    else:
        direction = "no_data"
    current_avg = points[-1]["avg_score"] if points else None
    return {
        "window_days": window_days,
        "direction": direction,
        "points": points,
        "current_avg": current_avg,
    }
