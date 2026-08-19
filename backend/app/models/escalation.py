"""
XYZ AI Backend — Escalation ORM Model

Represents a human-escalation ticket raised when the AI assistant
cannot resolve a query or the user explicitly asks for a human agent.

Statuses: OPEN → IN_PROGRESS → RESOLVED
"""

from datetime import datetime
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.user import get_utc_now


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="OPEN", server_default="OPEN", index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, server_default=func.now(),
        onupdate=get_utc_now, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Escalation id={self.id} user_id={self.user_id} status={self.status!r}>"
