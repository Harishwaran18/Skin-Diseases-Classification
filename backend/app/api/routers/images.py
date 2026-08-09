"""Image router: upload, list, get meta, serve bytes (owner-only), delete."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.ai import ImageUploadResponse
from app.schemas.ai import ImageOut  # noqa: F401
from app.services.image_service import (
    delete_image,
    get_image,
    image_path,
    list_images,
    upload_image,
)

router = APIRouter(prefix="/api/images", tags=["images"])


@router.post("/upload", response_model=ImageUploadResponse, status_code=201)
def upload(
    file: UploadFile = File(...),
    body_location: str | None = Form(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    img = upload_image(db, user, file, body_location)
    message = (
        "Image stored. Quality is sufficient."
        if img.quality_ok
        else (
            "Image stored but quality is insufficient for AI analysis "
            "(too blurry, dark, bright, or low resolution). Please retake "
            "in good lighting."
        )
    )
    return ImageUploadResponse(
        image_id=img.id,
        quality_ok=img.quality_ok,
        quality_score=img.quality_score,
        message=message,
    )


@router.get("", response_model=list[ImageOut])
def list_(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_images(db, user)


@router.get("/{image_id}", response_model=ImageOut)
def get_meta(
    image_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_image(db, user, image_id)


@router.get("/{image_id}/file")
def get_file(
    image_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    img = get_image(db, user, image_id)
    path = image_path(user.id, img.stored_filename)
    if not path.exists():
        return {"detail": "File missing from storage."}
    return FileResponse(
        str(path), media_type=img.content_type, filename=img.original_filename
    )


@router.delete("/{image_id}", status_code=200)
def remove(
    image_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_image(db, user, image_id)
