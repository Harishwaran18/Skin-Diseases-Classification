"""Skin image model with private storage + quality metadata."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class SkinImage(Base):
    __tablename__ = "skin_images"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    stored_filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    body_location: Mapped[str | None] = mapped_column(String(64))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    quality_score: Mapped[float | None] = mapped_column(Float)
    quality_ok: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    predictions: Mapped[list["AIPrediction"]] = relationship(  # noqa: F821
        back_populates="image", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship(back_populates="images")  # noqa: F821
