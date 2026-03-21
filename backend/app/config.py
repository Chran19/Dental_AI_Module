"""
Application configuration.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables."""

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Chairside Companion"
    APP_VERSION: str = "1.0.0-mvp"
    DEBUG: bool = False

    # ── Database (PostgreSQL) ────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chairside_companion"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 15  # FR-01.3: Session timeout

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Rate Limiting ────────────────────────────────────────────────────────
    AI_RATE_LIMIT_PER_DAY: int = 100  # FR-04.4

    # ── File Upload ──────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50  # FR-03.2
    MAX_REQUEST_BODY_MB: int = 1  # Module 1 §10: payload limit
    UPLOAD_DIR: str = "uploads"  # Directory for storing user uploaded files

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
