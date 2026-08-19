"""
XYZ AI Backend — FastAPI Application Entry Point

Creates the FastAPI app, configures CORS middleware,
and mounts the central API router.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.router import api_router
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Human-Like AI School Assistant — Backend API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with project info."""
    return {
        "project": settings.APP_NAME,
        "description": "Human-Like AI School Assistant",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
