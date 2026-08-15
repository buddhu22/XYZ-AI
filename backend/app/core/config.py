"""
XYZ AI Backend — Core Configuration

Uses pydantic-settings to load environment variables with type safety.
All secrets are read from environment / .env file — never hardcoded.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application ---
    APP_NAME: str = "XYZ AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/xyz_ai"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production"

    # --- Gemini AI (Phase 2+) ---
    GEMINI_API_KEY: str = ""

    # --- CORS ---
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()
