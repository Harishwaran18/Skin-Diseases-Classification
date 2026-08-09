"""Reports router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.report import ReportGenerate, ReportOut
from app.services.report_service import (
    generate_report,
    get_report,
    list_reports,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate", response_model=ReportOut, status_code=201)
def generate(
    payload: ReportGenerate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return generate_report(db, user, payload.date_from, payload.date_to, payload.include_images)


@router.get("", response_model=list[ReportOut])
def list_(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return list_reports(db, user)


@router.get("/{report_id}/download")
def download(
    report_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report, path = get_report(db, user, report_id)
    if not path.exists():
        return {"detail": "Report file missing."}
    return FileResponse(
        str(path),
        media_type="application/pdf",
        filename=f"skincare_report_{report.id}.pdf",
    )
