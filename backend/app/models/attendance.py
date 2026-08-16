from datetime import datetime, date
from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base
from app.models.user import get_utc_now

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_student_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # "present" or "absent"
    marked_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, server_default=func.now(), nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="attendance")
    marker: Mapped["User"] = relationship("User", back_populates="marked_attendance", foreign_keys=[marked_by])

    def __repr__(self) -> str:
        return f"<Attendance id={self.id} student_id={self.student_id} date={self.date} status={self.status!r}>"
