"""
XYZ AI Backend — Central API Router

Aggregates all route modules into a single router.
New route modules are added here — no need to modify main.py.
"""

from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()

# --- Health ---
api_router.include_router(health.router)

# Future routes will be included here:
# api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
