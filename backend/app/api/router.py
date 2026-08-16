"""
XYZ AI Backend — Central API Router

Aggregates all route modules into a single router.
New route modules are added here — no need to modify main.py.
"""

from fastapi import APIRouter

from app.api.routes import health
from app.api.v1 import students, parents, teachers, attendance

api_router = APIRouter()

# --- Health ---
api_router.include_router(health.router)

# --- Version 1 API ---
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(students.router, prefix="/students", tags=["Students"])
v1_router.include_router(parents.router, prefix="/parents", tags=["Parents"])
v1_router.include_router(teachers.router, prefix="/teachers", tags=["Teachers"])
v1_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])

api_router.include_router(v1_router)

