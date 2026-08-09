"""Symptom log model. Scale 0-5 per dimension."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Symptom(Base):
    __tablename__ = "symptoms"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    itching: Mapped[int] = mapped_column(Integer, default=0)
    redness: Mapped[int] = mapped_column(Integer, default=0)
    dryness: Mapped[int] = mapped_column(Integer, default=0)
    pain: Mapped[int] = mapped_column(Integer, default=0)
    swelling: Mapped[int] = mapped_column(Integer, default=0)
    irritation: Mapped[int] = mapped_column(Integer, default=0)
    burning: Mapped[int] = mapped_column(Integer, default=0)
    scaling: Mapped[int] = mapped_column(Integer, default=0)
    lesion_count: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="symptoms")  # noqa: F821

    @property
    def overall_score(self) -> int:
        """Average across all dimensions (0-5)."""
        vals = [
            self.itching, self.redness, self.dryness, self.pain,
            self.swelling, self.irritation, self.burning, self.scaling,
            min(self.lesion_count, 5),
        ]
        return round(sum(vals) / len(vals), 2)
