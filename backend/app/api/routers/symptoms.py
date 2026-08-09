"""Symptom router."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.symptom import (
    SymptomCreate,
    SymptomOut,
    SymptomTrendResponse,
)
from app.services.symptom_service import (
    compute_trend,
    create_symptom,
    list_symptoms,
)

router = APIRouter(prefix="/api/symptoms", tags=["symptoms"])


@router.post("", response_model=SymptomOut, status_code=201)
def add_symptom(
    payload: SymptomCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_none=True)
    return create_symptom(db, user, data)


@router.get("", response_model=list[SymptomOut])
def list_(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_symptoms(db, user, date_from, date_to)


@router.get("/trends", response_model=SymptomTrendResponse)
def trends(
    window: int = Query(default=30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return compute_trend(db, user, window)
