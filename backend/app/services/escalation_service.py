"""
XYZ AI Backend — Escalation Service

Business logic for creating and managing human escalation tickets.
Used when the AI cannot resolve a query or the user explicitly requests human help.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.escalation import Escalation
from app.schemas.escalation import EscalationCreate, EscalationStatus


def create_escalation(db: Session, payload: EscalationCreate) -> Escalation:
    """Create a new OPEN escalation ticket."""
    ticket = Escalation(
        user_id=payload.user_id,
        role=payload.role,
        reason=payload.reason,
        status=EscalationStatus.OPEN.value,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_escalations(
    db: Session,
    status_filter: Optional[EscalationStatus] = None,
    limit: int = 50,
) -> List[Escalation]:
    """List escalation tickets, optionally filtered by status."""
    query = db.query(Escalation)
    if status_filter:
        query = query.filter(Escalation.status == status_filter.value)
    return query.order_by(Escalation.created_at.desc()).limit(limit).all()


def get_escalation_by_id(db: Session, escalation_id: int) -> Optional[Escalation]:
    """Retrieve a single escalation ticket by ID."""
    return db.query(Escalation).filter(Escalation.id == escalation_id).first()


def update_escalation_status(
    db: Session, escalation_id: int, new_status: EscalationStatus
) -> Optional[Escalation]:
    """Transition an escalation ticket to a new status."""
    ticket = get_escalation_by_id(db, escalation_id)
    if ticket is None:
        return None
    ticket.status = new_status.value
    db.commit()
    db.refresh(ticket)
    return ticket
