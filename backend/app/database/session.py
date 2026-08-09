"""Database engine, session factory, and declarative Base."""
from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url, connect_args=connect_args, pool_pre_ping=True
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Create all tables. Called on application startup."""
    # Import models so they are registered on Base.metadata.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
