from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.db.base import Base
from app.models.user import get_utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.attendance import Attendance
    from app.models.parent import Parent, ParentStudent


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    class_name: Mapped[str] = mapped_column(String(50), nullable=False)
    section: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, server_default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="student")
    attendance: Mapped[List["Attendance"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    
    # Many-to-many relationship to parents via ParentStudent association
    parents: Mapped[List["Parent"]] = relationship(
        "Parent",
        secondary="parent_students",
        back_populates="students"
    )

    def __repr__(self) -> str:
        return f"<Student id={self.id} roll_number={self.roll_number!r} class={self.class_name!r} section={self.section!r}>"
