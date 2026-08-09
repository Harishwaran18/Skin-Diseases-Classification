"""Application configuration loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "SkinCare AI"
    # Database
    database_url: str = "sqlite:///./skincare.db"
    # JWT / Auth
    secret_key: str = "change-me-to-a-long-random-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080
    # AI
    ai_backend: str = "demo"
    ai_confidence_threshold: float = 0.55
    ai_model_path: str = ""
    # Image uploads
    upload_dir: str = "./uploads"
    max_image_bytes: int = 10 * 1024 * 1024
    # CORS
    backend_cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8080,http://127.0.0.1:8080,"
        "http://localhost:12001,http://127.0.0.1:12001"
    )
    # Ports (informational)
    backend_port: int = 12000
    frontend_port: int = 12001

    @property
    def cors_origins(self) -> list[str]:
        return [
            o.strip()
            for o in self.backend_cors_origins.split(",")
            if o.strip()
        ]

    @property
    def upload_path(self) -> Path:
        p = Path(self.upload_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return settings
