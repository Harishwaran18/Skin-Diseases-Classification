"""Symptom schemas. All scales 0-5."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.auth import ORMBase

_DIM = Field(default=0, ge=0, le=5)


class SymptomCreate(BaseModel):
    recorded_at: datetime | None = None
    itching: int = _DIM
    redness: int = _DIM
    dryness: int = _DIM
    pain: int = _DIM
    swelling: int = _DIM
    irritation: int = _DIM
    burning: int = _DIM
    scaling: int = _DIM
    lesion_count: int = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=2000)


class SymptomOut(ORMBase):
    id: str
    recorded_at: datetime
    itching: int
    redness: int
    dryness: int
    pain: int
    swelling: int
    irritation: int
    burning: int
    scaling: int
    lesion_count: int
    notes: str | None


class SymptomTrendPoint(BaseModel):
    date: str
    avg_score: float
    max_score: float
    count: int


class SymptomTrendResponse(BaseModel):
    window_days: int
    direction: str
    points: list[SymptomTrendPoint]
    current_avg: float | None
