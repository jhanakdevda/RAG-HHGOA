"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings. API keys are optional in this phase."""

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "HH Goa Voice RAG"
    debug: bool = False

    # Optional — required in later phases, not enforced now
    sarvam_api_key: str | None = None
    llm_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
