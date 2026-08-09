"""Image + AI prediction schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.auth import ORMBase


class ImageOut(ORMBase):
    id: str
    body_location: str | None
    width: int | None
    height: int | None
    quality_score: float | None
    quality_ok: bool
    original_filename: str
    notes: str | None
    created_at: datetime


class ImageUploadResponse(BaseModel):
    image_id: str
    quality_ok: bool
    quality_score: float | None
    message: str


class AIPredictionOut(ORMBase):
    id: str
    image_id: str
    category: str | None
    confidence: float
    severity: str | None
    severity_score: float | None
    model_version: str
    is_demo: bool
    reliable: bool
    disclaimer: str
    attention_note: str | None
    probabilities: dict[str, float] = {}
    created_at: datetime


class AIAnalyzeResponse(BaseModel):
    prediction: AIPredictionOut
    consultation_recommended: bool
    message: str
