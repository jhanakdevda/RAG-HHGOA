"""FastAPI application entry point."""

from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return service health status."""
    return {
        "status": "ok",
        "project": "HH Goa Voice RAG",
        "stage": "backend foundation",
    }
