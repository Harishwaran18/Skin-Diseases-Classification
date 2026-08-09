"""Report schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.auth import ORMBase


class ReportGenerate(BaseModel):
    date_from: datetime | None = None
    date_to: datetime | None = None
    include_images: bool = True


class ReportOut(ORMBase):
    id: str
    date_from: datetime
    date_to: datetime
    created_at: datetime
