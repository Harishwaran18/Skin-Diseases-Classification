"""Trigger schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.auth import ORMBase


class TriggerCategory(str, Enum):
    environment = "environment"
    lifestyle = "lifestyle"
    products = "products"
    food = "food"
    other = "other"


class TriggerCreate(BaseModel):
    recorded_at: datetime | None = None
    category: TriggerCategory
    name: str = Field(min_length=1, max_length=120)
    intensity: int = Field(default=0, ge=0, le=5)
    notes: str | None = Field(default=None, max_length=2000)


class TriggerOut(ORMBase):
    id: str
    recorded_at: datetime
    category: str
    name: str
    intensity: int
    notes: str | None


class TriggerAssociation(BaseModel):
    category: str
    name: str
    frequency: int
    mean_score_when_present: float
    mean_score_when_absent: float
    difference: float
    correlation: float
    summary: str


class TriggerAnalysisResponse(BaseModel):
    associations: list[TriggerAssociation]
    note: str
