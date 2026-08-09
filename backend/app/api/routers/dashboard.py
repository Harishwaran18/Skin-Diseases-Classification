"""Dashboard router: aggregated overview."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.ai_prediction import AIPrediction
from app.models.skin_image import SkinImage
from app.models.symptom import Symptom
from app.models.trigger import Trigger
from app.models.user import User
from app.schemas.dashboard import DashboardData
from app.services.analytics.risk import compute_risk
from app.services.analytics.trend import trend_summary
from app.services.treatment_service import overall_adherence, upcoming_reminders

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardData)
def dashboard(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_syms = list(
        db.scalars(
            select(Symptom).where(
                Symptom.user_id == user.id, Symptom.recorded_at >= today_start
            )
        )
    )
    if today_syms:
        scores = []
        for s in today_syms:
            dims = [getattr(s, d) for d in [
                "itching", "redness", "dryness", "pain", "swelling",
                "irritation", "burning", "scaling"]] + [min(s.lesion_count, 5)]
            scores.append(sum(dims) / len(dims))
        today_score = round(sum(scores) / len(scores), 2)
    else:
        today_score = None

    trend = trend_summary(db, user, 30)
    risk = compute_risk(db, user, 30)
    latest_img = db.scalar(
        select(SkinImage)
        .where(SkinImage.user_id == user.id)
        .order_by(SkinImage.created_at.desc())
    )
    recent_triggers = [
        {"name": t.name, "category": t.category, "intensity": t.intensity,
         "recorded_at": t.recorded_at.isoformat()}
        for t in db.scalars(
            select(Trigger)
            .where(Trigger.user_id == user.id)
            .order_by(Trigger.recorded_at.desc())
            .limit(5)
        )
    ]
    reminders = upcoming_reminders(db, user)
    last_pred = db.scalar(
        select(AIPrediction)
        .where(AIPrediction.user_id == user.id)
        .order_by(AIPrediction.created_at.desc())
    )
    count_30 = len(
        list(db.scalars(
            select(Symptom).where(
                Symptom.user_id == user.id,
                Symptom.recorded_at >= datetime.now(timezone.utc) - timedelta(days=30),
            )
        ))
    )
    return DashboardData(
        today_score=today_score,
        severity_trend=trend["direction"],
        adherence_pct=overall_adherence(db, user),
        risk_level=risk["level"],
        risk_message=risk["message"],
        latest_image_id=latest_img.id if latest_img else None,
        latest_image_url=f"/api/images/{latest_img.id}/file" if latest_img else None,
        recent_triggers=recent_triggers,
        upcoming_reminders=reminders,
        last_prediction_category=last_pred.category if last_pred else None,
        last_prediction_confidence=last_pred.confidence if last_pred else None,
        symptom_count_30d=count_30,
        updated_at=datetime.now(timezone.utc),
    )
