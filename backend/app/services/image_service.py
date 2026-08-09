"""Image service: secure upload, quality check, private storage, owner-only serving."""
from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.image_quality import check_quality
from app.core.config import settings
from app.models.skin_image import SkinImage
from app.models.user import User
from app.utils.errors import AppError, NotFoundError
from app.utils.ids import random_filename

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}


def _user_dir(user_id: str) -> Path:
    d = settings.upload_path / f"user_{user_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def upload_image(
    db: Session, user: User, file: UploadFile, body_location: str | None
) -> SkinImage:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise AppError(
            "Only JPG/JPEG/PNG images are accepted.", 415
        )
    data = file.file.read()
    if len(data) > settings.max_image_bytes:
        raise AppError(
            f"Image exceeds the maximum size of "
            f"{settings.max_image_bytes // (1024*1024)}MB.", 413
        )
    quality = check_quality(data)
    ext = "png" if file.content_type == "image/png" else "jpg"
    stored = random_filename(ext)
    dest = _user_dir(user.id) / stored
    dest.write_bytes(data)
    img = SkinImage(
        user_id=user.id,
        stored_filename=stored,
        original_filename=file.filename or "upload.jpg",
        content_type=file.content_type,
        size_bytes=len(data),
        body_location=body_location,
        width=quality["width"],
        height=quality["height"],
        quality_score=quality["score"],
        quality_ok=quality["ok"],
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


def list_images(db: Session, user: User) -> list[SkinImage]:
    return list(
        db.scalars(
            select(SkinImage)
            .where(SkinImage.user_id == user.id)
            .order_by(SkinImage.created_at.desc())
        )
    )


def get_image(db: Session, user: User, image_id: str) -> SkinImage:
    img = db.scalar(
        select(SkinImage).where(
            SkinImage.id == image_id, SkinImage.user_id == user.id
        )
    )
    if not img:
        raise NotFoundError("Image not found")
    return img


def image_path(user_id: str, stored_filename: str) -> Path:
    return _user_dir(user_id) / stored_filename


def delete_image(db: Session, user: User, image_id: str) -> dict:
    img = get_image(db, user, image_id)
    path = image_path(user.id, img.stored_filename)
    if path.exists():
        path.unlink()
    db.delete(img)
    db.commit()
    return {"detail": "Image deleted."}
