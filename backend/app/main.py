"""FastAPI application factory."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Make the repo-root `ml/` package importable from the backend.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import init_db

logger = logging.getLogger("skincare")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description=(
            "AI-assisted skin-health monitoring, symptom tracking, trigger "
            "analysis, treatment adherence, trend monitoring, AI image "
            "screening (demo/mock model), and doctor-friendly PDF reporting. "
            "This is a screening/monitoring/education tool — NOT a diagnostic "
            "device."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup() -> None:
        try:
            init_db()
            logger.info("Database initialized.")
        except Exception as exc:  # noqa: BLE001
            logger.error("DB init failed: %s", exc)

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
            "ai_backend": settings.ai_backend,
        }

    # Register routers
    from app.api.routers import (
        ai,
        auth,
        dashboard,
        images,
        profile,
        reports,
        symptoms,
        treatments,
        triggers,
    )

    app.include_router(auth.router)
    app.include_router(profile.router)
    app.include_router(symptoms.router)
    app.include_router(triggers.router)
    app.include_router(treatments.router)
    app.include_router(images.router)
    app.include_router(ai.router)
    app.include_router(reports.router)
    app.include_router(dashboard.router)

    return app


app = create_app()
