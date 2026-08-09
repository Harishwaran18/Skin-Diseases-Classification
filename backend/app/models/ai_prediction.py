"""AI prediction model — always labelled, with confidence + disclaimer."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    image_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("skin_images.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[str | None] = mapped_column(String(120))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str | None] = mapped_column(String(32))
    severity_score: Mapped[float | None] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(64))
    is_demo: Mapped[bool] = mapped_column(default=False)
    reliable: Mapped[bool] = mapped_column(default=True)
    disclaimer: Mapped[str] = mapped_column(Text)
    attention_note: Mapped[str | None] = mapped_column(Text)
    probabilities_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    image: Mapped["SkinImage"] = relationship(  # noqa: F821
        back_populates="predictions"
    )
