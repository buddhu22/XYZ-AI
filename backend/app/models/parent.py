from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.db.base import Base
from app.models.user import get_utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.student import Student


class ParentStudent(Base):
    __tablename__ = "parent_students"
    __table_args__ = (
        UniqueConstraint("parent_id", "student_id", name="uq_parent_student"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)


class Parent(Base):
    __tablename__ = "parents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, server_default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="parent")
    
    # Many-to-many relationship to students
    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary="parent_students",
        back_populates="parents"
    )

    def __repr__(self) -> str:
        return f"<Parent id={self.id} phone={self.phone!r}>"
