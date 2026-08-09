"""Auth router: register / login / logout / me."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User, UserProfile
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.utils.errors import AppError, UnauthorizedError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise AppError("Email already registered", status.HTTP_409_CONFLICT)
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id))
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, {"name": user.full_name})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        is_demo=user.is_demo,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    token = create_access_token(user.id, {"name": user.full_name})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        full_name=user.full_name,
        is_demo=user.is_demo,
    )


@router.post("/logout", status_code=200)
def logout(user: User = Depends(get_current_user)):
    # Stateless JWT: client discards the token. No server blocklist for the
    # prototype (documented limitation).
    return {"detail": "Logged out. Please discard your token client-side."}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
