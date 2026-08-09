"""FastAPI dependencies: DB session + current user via JWT."""
from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.services.auth_service import decode_token
from app.utils.errors import UnauthorizedError


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")
    user = db.get(User, user_id)
    if not user:
        raise UnauthorizedError("User not found")
    return user
