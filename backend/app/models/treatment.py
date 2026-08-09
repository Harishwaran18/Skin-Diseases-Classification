"""Treatment + adherence log models."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Treatment(Base):
    __tablename__ = "treatments"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(180))
    schedule: Mapped[str] = mapped_column(String(180))
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    logs: Mapped[list["TreatmentLog"]] = relationship(
        back_populates="treatment", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship(back_populates="treatments")  # noqa: F821


class TreatmentLog(Base):
    __tablename__ = "treatment_logs"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    treatment_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("treatments.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    status: Mapped[str] = mapped_column(String(16), default="completed")
    note: Mapped[str | None] = mapped_column(Text)

    treatment: Mapped["Treatment"] = relationship(back_populates="logs")
