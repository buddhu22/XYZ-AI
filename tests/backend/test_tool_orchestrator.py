"""
Unit test suite for Phase 4 Step 5 Tool Orchestrator & Gemini Tool Calling
"""

import pytest
import anyio
from unittest.mock import AsyncMock, patch

from app.ai.tool_orchestrator import execute_tool_with_security
from app.security.context import MOCK_STUDENT_CONTEXT, MOCK_TEACHER_CONTEXT


@pytest.mark.anyio
async def test_tool_orchestrator_authorized_student_call():
    user_context = MOCK_STUDENT_CONTEXT.to_dict()  # student_id = 1
    mock_attendance = {
        "student_id": 1,
        "student_name": "Aarav Sharma",
        "total_classes": 10,
        "present": 9,
        "absent": 1,
        "attendance_percentage": 90.0,
    }
    
    with patch("app.tools.attendance.erp_client.get_student_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_attendance
        res = await execute_tool_with_security("get_student_attendance", {"student_id": 1}, user_context)
        assert res["success"] is True
        assert res["attendance_percentage"] == 90.0


@pytest.mark.anyio
async def test_tool_orchestrator_blocked_student_marking_attendance():
    user_context = MOCK_STUDENT_CONTEXT.to_dict()
    res = await execute_tool_with_security(
        "mark_attendance", {"student_id": 1, "date": "2026-08-18", "status": "present"}, user_context
    )
    assert "error" in res
    assert "not authorized to mark attendance" in res["error"]


@pytest.mark.anyio
async def test_tool_orchestrator_blocked_student_accessing_other_student():
    user_context = MOCK_STUDENT_CONTEXT.to_dict()  # student_id = 1
    res = await execute_tool_with_security("get_student_attendance", {"student_id": 99}, user_context)
    assert "error" in res
    assert "only authorized to view your own attendance" in res["error"]


@pytest.mark.anyio
async def test_tool_orchestrator_teacher_mark_attendance_success():
    user_context = MOCK_TEACHER_CONTEXT.to_dict()
    mock_res = {"message": "Attendance marked successfully", "attendance_id": 10}
    
    with patch("app.tools.attendance.erp_client.mark_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_res
        res = await execute_tool_with_security(
            "mark_attendance", {"student_id": 1, "date": "2026-08-18", "status": "absent"}, user_context
        )
        assert res["success"] is True
        assert res["attendance_id"] == 10
