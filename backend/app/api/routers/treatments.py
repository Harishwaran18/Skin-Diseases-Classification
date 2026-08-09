"""Treatment router. System only reminds — never prescribes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.treatment import Treatment
from app.models.user import User
from app.schemas.treatment import (
    TreatmentCreate,
    TreatmentLogCreate,
    TreatmentLogOut,
    TreatmentOut,
    TreatmentUpdate,
)
from app.services.treatment_service import (
    _adherence,
    add_log,
    create_treatment,
    list_logs,
    list_treatments,
    update_treatment,
)

router = APIRouter(prefix="/api/treatments", tags=["treatments"])


def _out(t: Treatment, db: Session) -> TreatmentOut:
    return TreatmentOut(
        id=t.id,
        name=t.name,
        schedule=t.schedule,
        start_date=t.start_date,
        end_date=t.end_date,
        notes=t.notes,
        active=t.active,
        adherence_pct=_adherence(t, db),
    )


@router.post("", response_model=TreatmentOut, status_code=201)
def create(
    payload: TreatmentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    t = create_treatment(db, user, payload.model_dump(exclude_none=True))
    return _out(t, db)


@router.get("", response_model=list[TreatmentOut])
def list_(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    items = list_treatments(db, user)
    return [_out(t, db) for t in items]


@router.put("/{treatment_id}", response_model=TreatmentOut)
def update(
    treatment_id: str,
    payload: TreatmentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    t = update_treatment(db, user, treatment_id, payload.model_dump(exclude_unset=True))
    return _out(t, db)


@router.post("/{treatment_id}/logs", response_model=TreatmentLogOut, status_code=201)
def log_status(
    treatment_id: str,
    payload: TreatmentLogCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return add_log(
        db, user, treatment_id, payload.status.value, payload.note
    )


@router.get("/{treatment_id}/logs", response_model=list[TreatmentLogOut])
def logs(
    treatment_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_logs(db, user, treatment_id)
