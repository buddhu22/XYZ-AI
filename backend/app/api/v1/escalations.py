"""
XYZ AI Backend — Escalation REST Endpoints

Provides management staff with the ability to view and update
human-escalation tickets created by the AI assistant.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.escalation import (
    EscalationCreate,
    EscalationUpdate,
    EscalationResponse,
    EscalationStatus,
)
from app.services.escalation_service import (
    create_escalation,
    get_escalations,
    get_escalation_by_id,
    update_escalation_status,
)

router = APIRouter()


@router.post("", response_model=EscalationResponse, status_code=201, summary="Create escalation ticket")
def create_escalation_endpoint(
    payload: EscalationCreate,
    db: Session = Depends(get_db),
) -> EscalationResponse:
    """Create a new human-escalation ticket (called by the AI pipeline or staff)."""
    ticket = create_escalation(db, payload)
    return ticket


@router.get("", response_model=List[EscalationResponse], summary="List escalation tickets")
def list_escalations(
    status: Optional[EscalationStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[EscalationResponse]:
    """List escalation tickets with optional status filter."""
    return get_escalations(db, status_filter=status, limit=limit)


@router.get("/{escalation_id}", response_model=EscalationResponse, summary="Get escalation by ID")
def get_escalation(
    escalation_id: int,
    db: Session = Depends(get_db),
) -> EscalationResponse:
    """Retrieve a single escalation ticket by its ID."""
    ticket = get_escalation_by_id(db, escalation_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Escalation ticket not found")
    return ticket


@router.patch("/{escalation_id}", response_model=EscalationResponse, summary="Update escalation status")
def patch_escalation(
    escalation_id: int,
    payload: EscalationUpdate,
    db: Session = Depends(get_db),
) -> EscalationResponse:
    """Update the status of an escalation ticket (OPEN → IN_PROGRESS → RESOLVED)."""
    ticket = update_escalation_status(db, escalation_id, payload.status)
    if not ticket:
        raise HTTPException(status_code=404, detail="Escalation ticket not found")
    return ticket
