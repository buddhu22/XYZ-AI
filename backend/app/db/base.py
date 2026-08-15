"""
XYZ AI Backend — SQLAlchemy Base Model

All database models should inherit from this Base class.
Models will be added in Phase 2 (Student, Teacher, Parent, etc.).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass
