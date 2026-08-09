"""AI analysis router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.ai import AIAnalyzeResponse, AIPredictionOut
from app.services.ai_service import analyze_image, history

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/analyze/{image_id}", response_model=AIAnalyzeResponse)
def analyze(
    image_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return analyze_image(db, user, image_id)


@router.get("/history", response_model=list[AIPredictionOut])
def get_history(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return history(db, user)
