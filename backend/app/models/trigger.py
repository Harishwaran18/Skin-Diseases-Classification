"""Trigger model (environmental / lifestyle / products / food / other)."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Trigger(Base):
    __tablename__ = "triggers"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    category: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(120))
    intensity: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="triggers")  # noqa: F821
