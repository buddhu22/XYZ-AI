"""
Unit test suite for Phase 4 Step 4 User Context & Mock Auth Layer
"""

import pytest
from app.security.context import (
    UserContext,
    get_current_user_context,
    MOCK_STUDENT_CONTEXT,
    MOCK_PARENT_CONTEXT,
    MOCK_TEACHER_CONTEXT,
    MOCK_PRINCIPAL_CONTEXT,
)
from app.security.permissions import authorize_tool_execution


def test_user_context_defaults():
    ctx = get_current_user_context()
    assert ctx.role == "student"
    assert ctx.student_id == 1
    assert ctx.id == 101


def test_role_overrides():
    parent_ctx = get_current_user_context("parent")
    assert parent_ctx.role == "parent"
    assert parent_ctx.linked_children_ids == [1]

    teacher_ctx = get_current_user_context("teacher")
    assert teacher_ctx.role == "teacher"
    assert teacher_ctx.teacher_id == 1

    principal_ctx = get_current_user_context("principal")
    assert principal_ctx.role == "principal"


def test_context_integration_with_authorization():
    # 1. Student attempts mark attendance -> Denied
    student_ctx = get_current_user_context("student")
    auth_ok, error = authorize_tool_execution(
        student_ctx.to_dict(), "mark_attendance", {"student_id": 1}
    )
    assert auth_ok is False
    assert "not authorized to mark attendance" in error

    # 2. Teacher attempts mark attendance -> Authorized
    teacher_ctx = get_current_user_context("teacher")
    auth_ok, error = authorize_tool_execution(
        teacher_ctx.to_dict(), "mark_attendance", {"student_id": 1}
    )
    assert auth_ok is True
    assert error is None
