from functools import lru_cache
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent

# Deterministically load environment variables from project root and backend .env files.
# override=False ensures actual process environment variables take precedence over .env file values.
ROOT_ENV = PROJECT_ROOT / ".env"
BACKEND_ENV = BACKEND_DIR / ".env"

if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV, override=False)
if BACKEND_ENV.exists():
    load_dotenv(dotenv_path=BACKEND_ENV, override=False)


class Settings(BaseSettings):
    """Application settings including LLM configuration, Grounding thresholds, and CORS settings."""

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "HH Goa Voice RAG"
    debug: bool = False

    # Optional / Phase-specific API keys
    sarvam_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    cerebras_api_key: Optional[str] = None

    # LLM Provider Configuration
    llm_provider: str = "mock"  # Options: "mock", "gemini", "openai", "groq", "ollama", "cerebras"
    llm_model: str = "mock-v1"   # Provider model identifier
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_timeout: float = 3.0
    llm_temperature: float = 0.1

    # Phase 8 Grounding Verification Configurable Heuristic Thresholds
    grounding_grounded_threshold: float = 0.70
    grounding_partial_threshold: float = 0.45

    # Phase 9 Production CORS Configuration (Configurable via CORS_ORIGINS env)
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @property
    def effective_llm_api_key(self) -> Optional[str]:
        """Resolves LLM API key with precedence: explicit llm_api_key -> provider-specific key -> fallback."""
        if self.llm_api_key:
            return self.llm_api_key
        prov = (self.llm_provider or "").lower()
        if prov == "gemini":
            return self.gemini_api_key
        elif prov == "groq":
            return self.groq_api_key
        elif prov == "openai":
            return self.openai_api_key
        elif prov == "cerebras":
            return self.cerebras_api_key
        return self.gemini_api_key or self.groq_api_key or self.cerebras_api_key or self.openai_api_key


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
