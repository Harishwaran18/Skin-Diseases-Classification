"""AI service: orchestrates quality gate → classifier → safety layer."""
from __future__ import annotations

import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.safety import (
    DISCLAIMER,
    ATTENTION_NOTE,
    is_reliable,
    recommend_consultation,
    unreliable_message,
)
from app.models.ai_prediction import AIPrediction
from app.models.skin_image import SkinImage
from app.models.user import User
from app.services.image_service import get_image, image_path
from app.utils.errors import AppError, NotFoundError

logger = logging.getLogger("skincare.ai")


def analyze_image(db: Session, user: User, image_id: str) -> dict:
    img = get_image(db, user, image_id)
    if not img.quality_ok:
        raise AppError(
            "Image quality is insufficient for AI analysis. Please retake "
            "the image in good lighting.",
            422,
        )
    path = image_path(user.id, img.stored_filename)
    if not path.exists():
        raise NotFoundError("Image file missing from storage.")

    from ml.inference.classifier import get_classifier

    classifier = get_classifier()
    try:
        classifier.load_model()
        result = classifier.predict(path.read_bytes())
    except RuntimeError as exc:  # noqa: BLE001
        # torch backend unavailable → fall back to demo backend with notice.
        logger.warning("AI backend unavailable, falling back to demo: %s", exc)
        from ml.inference.demo_backend import DemoClassifier

        demo = DemoClassifier()
        demo.load_model()
        result = demo.predict(path.read_bytes())
        result.attention_note = (
            "Fallback to demo backend: " + (exc.args[0] if exc.args else "")
        )

    reliable = is_reliable(result.confidence)
    consultation = recommend_consultation(result.confidence, result.severity_score)

    pred = AIPrediction(
        user_id=user.id,
        image_id=img.id,
        category=result.category if reliable else None,
        confidence=round(result.confidence, 3),
        severity=result.severity if reliable else None,
        severity_score=result.severity_score if reliable else None,
        model_version=result.model_version,
        is_demo=result.is_demo,
        reliable=reliable,
        disclaimer=DISCLAIMER,
        attention_note=result.attention_note or ATTENTION_NOTE,
        probabilities_json=json.dumps(result.probabilities),
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    message = (
        unreliable_message()
        if not reliable
        else "AI screening complete. See the result and disclaimer below."
    )
    return {
        "prediction": _pred_out(pred),
        "consultation_recommended": consultation,
        "message": message,
    }


def history(db: Session, user: User) -> list[dict]:
    preds = list(
        db.scalars(
            select(AIPrediction)
            .where(AIPrediction.user_id == user.id)
            .order_by(AIPrediction.created_at.desc())
        )
    )
    return [_pred_out(p) for p in preds]


def _pred_out(p: AIPrediction) -> dict:
    probs = {}
    if p.probabilities_json:
        try:
            probs = json.loads(p.probabilities_json)
        except json.JSONDecodeError:
            probs = {}
    return {
        "id": p.id,
        "image_id": p.image_id,
        "category": p.category,
        "confidence": p.confidence,
        "severity": p.severity,
        "severity_score": p.severity_score,
        "model_version": p.model_version,
        "is_demo": p.is_demo,
        "reliable": p.reliable,
        "disclaimer": p.disclaimer,
        "attention_note": p.attention_note,
        "probabilities": probs,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
