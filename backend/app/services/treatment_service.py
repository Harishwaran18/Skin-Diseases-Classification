"""Treatment + adherence service."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.treatment import Treatment, TreatmentLog
from app.models.user import User
from app.utils.errors import NotFoundError


def _adherence(treatment: Treatment, db: Session, window_days: int = 30) -> float:
    since = datetime.now(timezone.utc) - timedelta(days=window_days)
    logs = list(
        db.scalars(
            select(TreatmentLog)
            .where(
                TreatmentLog.treatment_id == treatment.id,
                TreatmentLog.logged_at >= since,
            )
        )
    )
    if not logs:
        return 0.0
    completed = sum(1 for l in logs if l.status == "completed")
    return round(100 * completed / len(logs), 1)


def create_treatment(db: Session, user: User, data: dict) -> Treatment:
    t = Treatment(user_id=user.id, **data)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def list_treatments(db: Session, user: User) -> list[Treatment]:
    return list(
        db.scalars(
            select(Treatment)
            .where(Treatment.user_id == user.id)
            .order_by(Treatment.created_at.desc())
        )
    )


def update_treatment(
    db: Session, user: User, treatment_id: str, data: dict
) -> Treatment:
    t = db.scalar(
        select(Treatment).where(
            Treatment.id == treatment_id, Treatment.user_id == user.id
        )
    )
    if not t:
        raise NotFoundError("Treatment not found")
    for k, v in data.items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


def add_log(
    db: Session, user: User, treatment_id: str, status: str, note: str | None
) -> TreatmentLog:
    t = db.scalar(
        select(Treatment).where(
            Treatment.id == treatment_id, Treatment.user_id == user.id
        )
    )
    if not t:
        raise NotFoundError("Treatment not found")
    log = TreatmentLog(
        treatment_id=treatment_id, user_id=user.id, status=status, note=note
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_logs(db: Session, user: User, treatment_id: str) -> list[TreatmentLog]:
    return list(
        db.scalars(
            select(TreatmentLog)
            .where(
                TreatmentLog.treatment_id == treatment_id,
                TreatmentLog.user_id == user.id,
            )
            .order_by(TreatmentLog.logged_at.desc())
        )
    )


def overall_adherence(db: Session, user: User) -> float:
    treatments = list_treatments(db, user)
    if not treatments:
        return 0.0
    vals = [_adherence(t, db) for t in treatments]
    return round(sum(vals) / len(vals), 1)


def upcoming_reminders(db: Session, user: User) -> list[dict]:
    treatments = [
        t for t in list_treatments(db, user) if t.active and not t.end_date
    ]
    return [{"name": t.name, "schedule": t.schedule} for t in treatments]
