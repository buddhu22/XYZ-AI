"""
XYZ AI Backend — Escalation Schemas

Pydantic models for human escalation ticket creation, update, and API responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EscalationStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class EscalationCreate(BaseModel):
    """Payload to create a new escalation ticket."""
    user_id: int = Field(..., description="ID of the user requesting escalation")
    role: str = Field(..., description="Role of the requesting user")
    reason: str = Field(..., description="Reason / context for the escalation")


class EscalationUpdate(BaseModel):
    """Payload to update an existing escalation ticket."""
    status: EscalationStatus = Field(..., description="New status for the escalation")


class EscalationResponse(BaseModel):
    """API response representation of an escalation ticket."""
    id: int
    user_id: int
    role: str
    reason: str
    status: EscalationStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
