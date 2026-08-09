"""SQLAlchemy ORM models (spec Section 28 schema)."""
from __future__ import annotations
from app.models.user import User, UserProfile
from app.models.symptom import Symptom
from app.models.trigger import Trigger
from app.models.skin_image import SkinImage
from app.models.ai_prediction import AIPrediction
from app.models.treatment import Treatment, TreatmentLog
from app.models.report import Report

__all__ = [
    "User",
    "UserProfile",
    "Symptom",
    "Trigger",
    "SkinImage",
    "AIPrediction",
    "Treatment",
    "TreatmentLog",
    "Report",
]
