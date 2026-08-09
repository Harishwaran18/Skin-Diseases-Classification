"""Profile schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.auth import ORMBase


class ProfileUpdate(BaseModel):
    age: int | None = Field(default=None, ge=0, le=130)
    gender: str | None = Field(default=None, max_length=32)
    known_condition: str | None = Field(default=None, max_length=255)
    allergies: str | None = Field(default=None, max_length=2000)
    current_treatments: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)


class ProfileOut(ORMBase):
    id: str
    user_id: str
    age: int | None
    gender: str | None
    known_condition: str | None
    allergies: str | None
    current_treatments: str | None
    notes: str | None
    updated_at: datetime
