from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.db.base import Base
from app.models.user import get_utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.attendance import Attendance


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, server_default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="teacher")

    def __repr__(self) -> str:
        return f"<Teacher id={self.id} employee_id={self.employee_id!r} subject={self.subject!r}>"
