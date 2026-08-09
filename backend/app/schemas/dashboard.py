"""Dashboard aggregation schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DashboardData(BaseModel):
    today_score: float | None
    severity_trend: str
    adherence_pct: float
    risk_level: str
    risk_message: str
    latest_image_id: str | None
    latest_image_url: str | None
    recent_triggers: list[dict]
    upcoming_reminders: list[dict]
    last_prediction_category: str | None
    last_prediction_confidence: float | None
    symptom_count_30d: int
    updated_at: datetime
