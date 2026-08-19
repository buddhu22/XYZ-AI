"""
XYZ AI Backend — Phase 4 Comprehensive 12-Scenario End-to-End Test Suite

Verifies all 12 core functional, security, clarification, and error scenarios:
    1. Student viewing own attendance
    2. Student attempting to view another student's attendance
    3. Student attempting to mark attendance
    4. Parent viewing linked child's attendance
    5. Parent attempting to view unrelated student
    6. Teacher marking authorized attendance
    7. Principal viewing overall attendance
    8. Missing date clarification
    9. Missing student clarification
    10. ERP API failure
    11. Student not found
    12. Unauthorized tool execution
"""

import pytest
import anyio
from unittest.mock import AsyncMock, patch

from app.security.context import (
    MOCK_STUDENT_CONTEXT,
    MOCK_PARENT_CONTEXT,
    MOCK_TEACHER_CONTEXT,
    MOCK_PRINCIPAL_CONTEXT,
)
from app.ai.tool_orchestrator import execute_tool_with_security
from app.tools.attendance import (
    get_student_attendance,
    get_child_attendance,
    mark_attendance,
    get_overall_attendance,
)
from app.ai.clarification import check_clarification_needed, get_missing_fields
from app.ai.intent import IntentType
from app.ai.entities import ExtractedEntities
from app.services.erp_client import ERPClientError
from app.utils.error_handler import format_user_friendly_error


# =============================================================================
# SCENARIO 1: Student viewing own attendance (Authorized)
# =============================================================================
@pytest.mark.anyio
async def test_scenario_1_student_view_own_attendance():
    user_context = MOCK_STUDENT_CONTEXT.to_dict()  # student_id = 1
    mock_payload = {
        "student_id": 1,
        "student_name": "Aarav Sharma",
        "total_classes": 20,
        "present": 18,
        "absent": 2,
        "attendance_percentage": 90.0,
    }
    with patch("app.tools.attendance.erp_client.get_student_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_payload
        result = await execute_tool_with_security("get_student_attendance", {"student_id": 1}, user_context)
        assert result["success"] is True
        assert result["student_id"] == 1
        assert result["attendance_percentage"] == 90.0


# =============================================================================
# SCENARIO 2: Student attempting to view another student's attendance (Blocked)
# =============================================================================
@pytest.mark.anyio
async def test_scenario_2_student_view_other_student_attendance_blocked():
    user_context = MOCK_STUDENT_CONTEXT.to_dict()  # student_id = 1
    result = await execute_tool_with_security("get_student_attendance", {"student_id": 99}, user_context)
    assert "error" in result
    assert "only authorized to view your own attendance" in result["error"]


# =============================================================================
# SCENARIO 3: Student attempting to mark attendance (Blocked by RBAC)
# =============================================================================
@pytest.mark.anyio
async def test_scenario_3_student_mark_attendance_blocked():
    user_context = MOCK_STUDENT_CONTEXT.to_dict()
    result = await execute_tool_with_security(
        "mark_attendance", {"student_id": 1, "date": "2026-08-18", "status": "present"}, user_context
    )
    assert "error" in result
    assert "not authorized to mark attendance" in result["error"]


# =============================================================================
# SCENARIO 4: Parent viewing linked child's attendance (Authorized)
# =============================================================================
@pytest.mark.anyio
async def test_scenario_4_parent_view_linked_child_attendance():
    user_context = MOCK_PARENT_CONTEXT.to_dict()  # linked_children_ids = [1]
    mock_payload = {
        "student_id": 1,
        "student_name": "Aarav Sharma",
        "total_classes": 20,
        "present": 19,
        "absent": 1,
        "attendance_percentage": 95.0,
    }
    with patch("app.tools.attendance.erp_client.get_child_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_payload
        result = await execute_tool_with_security("get_child_attendance", {"student_id": 1}, user_context)
        assert result["success"] is True
        assert result["student_name"] == "Aarav Sharma"
        assert result["attendance_percentage"] == 95.0


# =============================================================================
# SCENARIO 5: Parent attempting to view unrelated student (Blocked by Ownership)
# =============================================================================
@pytest.mark.anyio
async def test_scenario_5_parent_view_unrelated_student_blocked():
    user_context = MOCK_PARENT_CONTEXT.to_dict()  # linked_children_ids = [1]
    result = await execute_tool_with_security("get_child_attendance", {"student_id": 999}, user_context)
    assert "error" in result
    assert "only view attendance for your linked children" in result["error"]


# =============================================================================
# SCENARIO 6: Teacher marking authorized attendance (Authorized)
# =============================================================================
@pytest.mark.anyio
async def test_scenario_6_teacher_mark_authorized_attendance():
    user_context = MOCK_TEACHER_CONTEXT.to_dict()
    mock_payload = {"message": "Attendance marked successfully", "attendance_id": 105}
    with patch("app.tools.attendance.erp_client.mark_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_payload
        result = await execute_tool_with_security(
            "mark_attendance", {"student_id": 1, "date": "2026-08-18", "status": "present"}, user_context
        )
        assert result["success"] is True
        assert result["attendance_id"] == 105
        assert result["status"] == "present"


# =============================================================================
# SCENARIO 7: Principal viewing overall attendance (Authorized)
# =============================================================================
@pytest.mark.anyio
async def test_scenario_7_principal_view_overall_attendance():
    user_context = MOCK_PRINCIPAL_CONTEXT.to_dict()
    mock_payload = {
        "total_students": 500,
        "total_records": 5000,
        "present": 4800,
        "absent": 200,
        "overall_attendance_percentage": 96.0,
    }
    with patch("app.tools.attendance.erp_client.get_overall_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_payload
        result = await execute_tool_with_security("get_overall_attendance", {}, user_context)
        assert result["success"] is True
        assert result["total_students"] == 500
        assert result["overall_attendance_percentage"] == 96.0


# =============================================================================
# SCENARIO 8: Missing date clarification
# =============================================================================
def test_scenario_8_missing_date_clarification():
    entities = ExtractedEntities(student_name="Rahul", status="absent")  # missing date
    missing = get_missing_fields(IntentType.MARK_ATTENDANCE, entities, role="teacher")
    assert "date" in missing


# =============================================================================
# SCENARIO 9: Missing student clarification
# =============================================================================
def test_scenario_9_missing_student_clarification():
    entities = ExtractedEntities()  # missing student name / id
    missing = get_missing_fields(IntentType.VIEW_CHILD_ATTENDANCE, entities, role="parent")
    assert "student_name" in missing


# =============================================================================
# SCENARIO 10: ERP API failure (503 Service Unavailable)
# =============================================================================
def test_scenario_10_erp_api_failure():
    user_msg = format_user_friendly_error(status_code=503)
    assert "unavailable" in user_msg.lower()
    assert "try again" in user_msg.lower()


# =============================================================================
# SCENARIO 11: Student not found (404 Not Found)
# =============================================================================
def test_scenario_11_student_not_found():
    user_msg = format_user_friendly_error(status_code=404)
    assert "could not find" in user_msg.lower()
    assert "student" in user_msg.lower()


# =============================================================================
# SCENARIO 12: Unauthorized tool execution interception
# =============================================================================
@pytest.mark.anyio
async def test_scenario_12_unauthorized_tool_execution():
    user_context = {"id": 999, "role": "student", "student_id": 10}
    # Student trying to call get_overall_attendance
    res = await execute_tool_with_security("get_overall_attendance", {}, user_context)
    assert "error" in res
    assert "Access denied" in res["error"]
