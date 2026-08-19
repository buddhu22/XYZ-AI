"""
XYZ AI Backend — Authentication Schemas

Defines Pydantic models for user login, JWT tokens, and user profile payloads.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Payload to authenticate a user."""
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's plaintext password")
    role: Optional[str] = Field(None, description="Optional role validation requirement")


class ChildInfo(BaseModel):
    """Summary of a student child linked to a parent."""
    id: int
    name: str
    class_name: Optional[str] = None
    section: Optional[str] = None
    roll_number: Optional[str] = None


class UserInfo(BaseModel):
    """User profile information returned upon login or /me query."""
    id: int
    name: str
    email: str
    role: str
    student_id: Optional[int] = None
    parent_id: Optional[int] = None
    teacher_id: Optional[int] = None
    linked_children: List[ChildInfo] = Field(default_factory=list)


class TokenResponse(BaseModel):
    """Response returned upon successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
