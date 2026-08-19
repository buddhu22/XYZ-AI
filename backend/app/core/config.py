"""
XYZ AI Backend — Core Configuration

Uses pydantic-settings to load environment variables with type safety.
All secrets are read from environment / .env file — never hardcoded.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application ---
    APP_NAME: str = "XYZ AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/xyz_ai"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production"

    # --- Gemini AI ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    # --- ERP Backend ---
    ERP_BASE_URL: str = "http://127.0.0.1:8000"

    # --- CORS ---
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- Deployment ---
    ALLOWED_HOSTS: List[str] = ["*"]

    @model_validator(mode="after")
    def _warn_insecure_defaults(self) -> "Settings":
        """Log warnings for known-insecure defaults when DEBUG is off."""
        if not self.DEBUG:
            import logging
            _log = logging.getLogger("app.core.config")
            if self.SECRET_KEY == "change-me-in-production":
                _log.warning("SECRET_KEY is using the insecure default — set it in .env for production!")
            if not self.GEMINI_API_KEY:
                _log.warning("GEMINI_API_KEY is empty — AI features will not work.")
        return self


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()

