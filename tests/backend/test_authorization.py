"""
Unit test suite for Phase 4 Step 3 Role-Based Authorization & Ownership Layer
"""

import pytest
from app.security.permissions import (
    is_tool_allowed_for_role,
    authorize_tool_execution,
)


def test_student_view_own_attendance_authorized():
    user_context = {"id": 101, "role": "student", "student_id": 1}
    tool_kwargs = {"student_id": 1}
    authorized, error = authorize_tool_execution(user_context, "get_student_attendance", tool_kwargs)
    assert authorized is True
    assert error is None


def test_student_view_other_student_attendance_denied():
    user_context = {"id": 101, "role": "student", "student_id": 1}
    tool_kwargs = {"student_id": 2}  # Attempting to view student 2
    authorized, error = authorize_tool_execution(user_context, "get_student_attendance", tool_kwargs)
    assert authorized is False
    assert "only authorized to view your own attendance" in error


def test_student_mark_attendance_denied():
    user_context = {"id": 101, "role": "student", "student_id": 1}
    tool_kwargs = {"student_id": 1, "date": "2026-08-18", "status": "present"}
    authorized, error = authorize_tool_execution(user_context, "mark_attendance", tool_kwargs)
    assert authorized is False
    assert "not authorized to mark attendance" in error


def test_parent_view_linked_child_attendance_authorized():
    user_context = {"id": 201, "role": "parent", "parent_id": 10, "linked_children_ids": [1, 5]}
    tool_kwargs = {"student_id": 5}
    authorized, error = authorize_tool_execution(user_context, "get_child_attendance", tool_kwargs)
    assert authorized is True
    assert error is None


def test_parent_view_unrelated_student_attendance_denied():
    user_context = {"id": 201, "role": "parent", "parent_id": 10, "linked_children_ids": [1, 5]}
    tool_kwargs = {"student_id": 99}  # Unrelated student 99
    authorized, error = authorize_tool_execution(user_context, "get_child_attendance", tool_kwargs)
    assert authorized is False
    assert "only view attendance for your linked children" in error


def test_teacher_mark_attendance_authorized():
    user_context = {"id": 301, "role": "teacher", "teacher_id": 1}
    tool_kwargs = {"student_id": 1, "date": "2026-08-18", "status": "absent"}
    authorized, error = authorize_tool_execution(user_context, "mark_attendance", tool_kwargs)
    assert authorized is True
    assert error is None


def test_principal_view_overall_attendance_authorized():
    user_context = {"id": 401, "role": "principal"}
    tool_kwargs = {}
    authorized, error = authorize_tool_execution(user_context, "get_overall_attendance", tool_kwargs)
    assert authorized is True
    assert error is None
