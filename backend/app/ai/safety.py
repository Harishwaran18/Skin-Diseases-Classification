"""AI safety layer (spec Sections 14, 17, 36).

Enforces: confidence threshold, always-present disclaimer, consultation
recommendation, no diagnostic assertions, no prescribing.
"""
from __future__ import annotations

from app.core.config import settings

DISCLAIMER = (
    "This is an AI-assisted screening estimate from a prototype model for "
    "educational and monitoring purposes only. It is NOT a medical "
    "diagnosis. Skin conditions can look alike and only a qualified "
    "healthcare professional can diagnose and treat. Do not start, stop, "
    "or change any treatment based on this result."
)

ATTENTION_NOTE = (
    "AI attention visualization, when shown, is a technical artifact "
    "indicating which image regions influenced the model — it is NOT a "
    "medical explanation of your condition."
)


def is_reliable(confidence: float) -> bool:
    return confidence >= settings.ai_confidence_threshold


def recommend_consultation(confidence: float, severity_score: float | None) -> bool:
    if not is_reliable(confidence):
        return True
    if severity_score is not None and severity_score >= 0.7:
        return True
    return False


def unreliable_message() -> str:
    return (
        "Unable to provide reliable screening for this image. The model's "
        "confidence is below the reliability threshold. Please consult a "
        "qualified healthcare professional rather than relying on this "
        "result."
    )
