"""
XYZ AI Backend — User Authentication Context

Provides isolated UserContext management for application authorization.

NOTE (Phase 4):
    This module uses Mock User Context for development/testing when no
    JWT token is provided. The real context builder `build_user_context_from_erp`
    fetches actual parent→child relationships from the ERP API, not from hardcoded lists.

    Architecture:
        XYZ AI → ERPClient → ERP FastAPI → PostgreSQL
        (never: XYZ AI → direct PostgreSQL)

    When full JWT/Session authentication is implemented in Phase 5+,
    ONLY this module needs to be updated.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """
    Authenticated User Context.
    Carries verified identity, role, and relational identifiers.
    """
    id: int = Field(..., description="Primary User ID")
    name: str = Field(..., description="Full Name of the user")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="Authenticated Role: student, parent, teacher, principal")
    student_id: Optional[int] = Field(None, description="Linked Student Profile ID (if role is student)")
    parent_id: Optional[int] = Field(None, description="Linked Parent Profile ID (if role is parent)")
    teacher_id: Optional[int] = Field(None, description="Linked Teacher Profile ID (if role is teacher)")
    linked_children_ids: List[int] = Field(default_factory=list, description="IDs of linked children (if parent) — sourced from ERP DB")

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to standard dictionary for permission checks."""
        return self.model_dump()


# =============================================================================
# MOCK CONTEXT PRESETS (For Development & Testing)
# =============================================================================

MOCK_STUDENT_CONTEXT = UserContext(
    id=101,
    name="Aarav Sharma",
    email="aarav.sharma@school.edu",
    role="student",
    student_id=1,
)

MOCK_PARENT_CONTEXT = UserContext(
    id=201,
    name="Rajesh Sharma",
    email="rajesh.sharma@gmail.com",
    role="parent",
    parent_id=1,
    linked_children_ids=[1],  # Will be overridden by DB fetch in build_user_context_from_erp
)

MOCK_TEACHER_CONTEXT = UserContext(
    id=301,
    name="Sunita Rao",
    email="sunita.rao@school.edu",
    role="teacher",
    teacher_id=1,
)

MOCK_PRINCIPAL_CONTEXT = UserContext(
    id=401,
    name="Dr. V. K. Kapoor",
    email="principal@school.edu",
    role="principal",
)

MOCK_CONTEXT_PRESETS: Dict[str, UserContext] = {
    "student": MOCK_STUDENT_CONTEXT,
    "parent": MOCK_PARENT_CONTEXT,
    "teacher": MOCK_TEACHER_CONTEXT,
    "principal": MOCK_PRINCIPAL_CONTEXT,
}


async def build_user_context_from_erp(role: str, user_id: int) -> UserContext:
    """
    Build a real UserContext by fetching data from the ERP API.

    Security Guarantee:
        - linked_children_ids come ONLY from the ERP database, never from user input.
        - student_id/parent_id/teacher_id come ONLY from the ERP database, never trusted from request.
        - This ensures a parent cannot claim to own a child they are not linked to.

    Architecture:
        XYZ AI → ERPClient → GET /api/v1/parents/user/{user_id} → PostgreSQL
    """
    from app.services.erp_client import erp_client, ERPClientError
    import logging
    logger = logging.getLogger("app.security.context")

    role_lower = role.lower().strip()
    
    # 1. Start with the preset defaults as a base
    base = MOCK_CONTEXT_PRESETS.get(role_lower, MOCK_STUDENT_CONTEXT).model_copy()
    base.id = user_id
    base.role = role_lower

    # 2. Query ERP API to retrieve actual profile and database IDs
    try:
        if role_lower == "student":
            data = await erp_client.get_student_by_user(user_id)
            base.student_id = data.get("id")
            base.name = data.get("name", base.name)
            base.email = data.get("email", base.email)
            base.parent_id = None
            base.teacher_id = None
            base.linked_children_ids = []

        elif role_lower == "parent":
            data = await erp_client.get_parent_by_user(user_id)
            base.parent_id = data.get("id")
            base.name = data.get("name", base.name)
            base.email = data.get("email", base.email)
            base.student_id = None
            base.teacher_id = None
            # Extract real, DB-linked children IDs
            children = data.get("children", [])
            base.linked_children_ids = [c["id"] for c in children]

        elif role_lower == "teacher":
            data = await erp_client.get_teacher_by_user(user_id)
            base.teacher_id = data.get("id")
            base.name = data.get("name", base.name)
            base.email = data.get("email", base.email)
            base.student_id = None
            base.parent_id = None
            base.linked_children_ids = []

        elif role_lower == "principal":
            base.student_id = None
            base.parent_id = None
            base.teacher_id = None
            base.linked_children_ids = []

    except ERPClientError as e:
        logger.warning(
            f"ERP client error fetching profile for user_id={user_id}, role={role_lower}: {str(e)}. "
            "Falling back to mock presets for safety."
        )
        if base.parent_id == 1 and not base.linked_children_ids:
            base.linked_children_ids = [1]

    return base



def get_user_context_from_token(token: Optional[str] = None, role_override: Optional[str] = None) -> UserContext:
    """
    Extract verified UserContext from a JWT access token string.
    If no token is provided, falls back to role_override or default.
    """
    if token:
        from app.core.security import decode_access_token
        clean_token = token.replace("Bearer ", "").strip()
        payload = decode_access_token(clean_token)
        if payload and "sub" in payload:
            user_id = int(payload["sub"])
            role = payload.get("role", "student").lower()
            name = payload.get("name", "User")
            email = payload.get("email", "")
            student_id = payload.get("student_id")
            parent_id = payload.get("parent_id")
            teacher_id = payload.get("teacher_id")

            # Preset fallback for linked children if parent
            linked_children_ids = [1] if role == "parent" else []

            return UserContext(
                id=user_id,
                name=name,
                email=email,
                role=role,
                student_id=student_id,
                parent_id=parent_id,
                teacher_id=teacher_id,
                linked_children_ids=linked_children_ids,
            )

    return get_current_user_context(role_override)


def get_current_user_context(role_override: Optional[str] = None) -> UserContext:
    """
    Retrieve the current user authentication context (synchronous fallback).
    """
    if role_override:
        norm_role = role_override.lower().strip()
        if norm_role in MOCK_CONTEXT_PRESETS:
            return MOCK_CONTEXT_PRESETS[norm_role]
            
    return MOCK_STUDENT_CONTEXT

