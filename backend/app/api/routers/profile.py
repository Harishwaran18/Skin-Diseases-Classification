"""Profile router: read / update / delete / data export."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User, UserProfile
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.utils.errors import NotFoundError

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _get_or_create_profile(db: Session, user: User) -> UserProfile:
    if not user.profile:
        user.profile = UserProfile(user_id=user.id)
        db.flush()
    return user.profile


@router.get("", response_model=ProfileOut)
def get_profile(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return _get_or_create_profile(db, user)


@router.put("", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(db, user)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/export")
def export_data(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Export all of the user's data as JSON (privacy: data portability)."""
    from app.models import (
        AIPrediction,
        SkinImage,
        Symptom,
        Treatment,
        TreatmentLog,
        Trigger,
    )

    profile = _get_or_create_profile(db, user)
    symptoms = db.scalars(
        select(Symptom).where(Symptom.user_id == user.id).order_by(Symptom.recorded_at)
    ).all()
    triggers = db.scalars(
        select(Trigger).where(Trigger.user_id == user.id).order_by(Trigger.recorded_at)
    ).all()
    images = db.scalars(
        select(SkinImage).where(SkinImage.user_id == user.id).order_by(SkinImage.created_at)
    ).all()
    treatments = db.scalars(
        select(Treatment).where(Treatment.user_id == user.id)
    ).all()
    preds = db.scalars(
        select(AIPrediction).where(AIPrediction.user_id == user.id)
    ).all()
    logs = db.scalars(
        select(TreatmentLog).where(TreatmentLog.user_id == user.id)
    ).all()

    def _dts(obj):
        return obj.isoformat() if isinstance(obj, datetime) else obj

    def _to_dict(o, keys):
        return {k: _dts(getattr(o, k, None)) for k in keys}

    export = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user": _to_dict(user, ["id", "email", "full_name", "is_demo", "created_at"]),
        "profile": _to_dict(
            profile,
            [
                "id", "age", "gender", "known_condition", "allergies",
                "current_treatments", "notes", "updated_at",
            ],
        ),
        "symptoms": [
            _to_dict(s, [
                "id", "recorded_at", "itching", "redness", "dryness", "pain",
                "swelling", "irritation", "burning", "scaling", "lesion_count", "notes",
            ])
            for s in symptoms
        ],
        "triggers": [
            _to_dict(t, ["id", "recorded_at", "category", "name", "intensity", "notes"])
            for t in triggers
        ],
        "images": [
            _to_dict(im, [
                "id", "body_location", "quality_score", "quality_ok",
                "original_filename", "created_at",
            ])
            for im in images
        ],
        "treatments": [
            _to_dict(tr, [
                "id", "name", "schedule", "start_date", "end_date", "notes", "active",
            ])
            for tr in treatments
        ],
        "treatment_logs": [
            _to_dict(lg, ["id", "treatment_id", "logged_at", "status", "note"])
            for lg in logs
        ],
        "ai_predictions": [
            _to_dict(p, [
                "id", "image_id", "category", "confidence", "severity",
                "severity_score", "model_version", "is_demo", "reliable",
                "disclaimer", "attention_note", "created_at",
            ])
            for p in preds
        ],
    }
    return JSONResponse(
        content=export,
        headers={
            "Content-Disposition": f'attachment; filename="skincare_export_{user.id}.json"'
        },
    )


@router.delete("", status_code=200)
def delete_account(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete account + all associated data (privacy: right to erasure).

    Image files on disk are also removed.
    """
    from pathlib import Path

    from app.core.config import settings

    user_dir = Path(settings.upload_dir) / f"user_{user.id}"
    if user_dir.exists():
        for f in user_dir.glob("*"):
            try:
                f.unlink()
            except OSError:
                pass
        try:
            user_dir.rmdir()
        except OSError:
            pass
    db.delete(user)
    db.commit()
    return {"detail": "Account and all associated data have been deleted."}
