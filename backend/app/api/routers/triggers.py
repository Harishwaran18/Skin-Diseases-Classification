"""Trigger router."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.trigger import Trigger
from app.models.user import User
from app.schemas.trigger import (
    TriggerAnalysisResponse,
    TriggerCreate,
    TriggerOut,
)
from app.services.analytics.trigger_correlation import analyze_triggers

router = APIRouter(prefix="/api/triggers", tags=["triggers"])


@router.post("", response_model=TriggerOut, status_code=201)
def add_trigger(
    payload: TriggerCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_none=True)
    data["category"] = payload.category.value
    t = Trigger(user_id=user.id, **data)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("", response_model=list[TriggerOut])
def list_(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = select(Trigger).where(Trigger.user_id == user.id)
    if date_from:
        q = q.where(Trigger.recorded_at >= date_from)
    if date_to:
        q = q.where(Trigger.recorded_at <= date_to)
    q = q.order_by(Trigger.recorded_at.desc())
    return list(db.scalars(q))


@router.get("/analysis", response_model=TriggerAnalysisResponse)
def analysis(
    window: int = Query(default=30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return analyze_triggers(db, user, window)
