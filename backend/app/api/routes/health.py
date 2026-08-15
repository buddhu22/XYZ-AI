"""
XYZ AI Backend — Health Check Route

Simple health endpoint to verify the backend is running.
Used by the frontend to display connectivity status.
"""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["Health"])

settings = get_settings()


@router.get("/health")
async def health_check() -> dict:
    """Return backend health status."""
    return {
        "status": "healthy",
        "service": "xyz-ai-backend",
        "version": settings.APP_VERSION,
    }
