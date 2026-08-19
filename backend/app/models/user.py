import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.parent import Parent
    from app.models.teacher import Teacher
    from app.models.attendance import Attendance


class UserRole(str, enum.Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    PRINCIPAL = "principal"


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, server_default=func.now(), nullable=False)

    # One-to-one relationships to specific role profiles
    student: Mapped["Student"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    parent: Mapped["Parent"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher: Mapped["Teacher"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Attendance marked by this user
    marked_attendance: Mapped[list["Attendance"]] = relationship(
        "Attendance",
        back_populates="marker",
        foreign_keys="[Attendance.marked_by]"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} role={self.role.value!r}>"
