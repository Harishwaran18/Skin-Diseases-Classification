"""Treatment + adherence schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.auth import ORMBase


class TreatmentStatus(str, Enum):
    completed = "completed"
    skipped = "skipped"
    missed = "missed"


class TreatmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    schedule: str = Field(min_length=1, max_length=180)
    end_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=2000)


class TreatmentUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=180)
    schedule: str | None = Field(default=None, max_length=180)
    end_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=2000)
    active: bool | None = None


class TreatmentOut(ORMBase):
    id: str
    name: str
    schedule: str
    start_date: datetime
    end_date: datetime | None
    notes: str | None
    active: bool
    adherence_pct: float = 0.0


class TreatmentLogCreate(BaseModel):
    status: TreatmentStatus = TreatmentStatus.completed
    note: str | None = Field(default=None, max_length=2000)


class TreatmentLogOut(ORMBase):
    id: str
    treatment_id: str
    logged_at: datetime
    status: str
    note: str | None
