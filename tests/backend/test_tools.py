"""
XYZ AI Backend — Tool Layer Tests (Phase 4 Updated)
Tests attendance tool schemas, inputs, and ERP client responses.
"""

import pytest
import anyio
from unittest.mock import AsyncMock, patch

from app.tools.attendance import (
    get_student_attendance,
    get_child_attendance,
    mark_attendance,
    get_overall_attendance,
)
from app.tools.students import tool_find_student_by_name


@pytest.mark.anyio
async def test_get_student_attendance_success():
    mock_data = {
        "student_id": 1,
        "student_name": "Rahul Sharma",
        "total_classes": 2,
        "present": 1,
        "absent": 1,
        "attendance_percentage": 50.0,
    }
    with patch("app.tools.attendance.erp_client.get_student_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_data
        result = await get_student_attendance(1)
        assert result.get("success") is True
        assert result["student_name"] == "Rahul Sharma"
        assert result["attendance_percentage"] == 50.0


@pytest.mark.anyio
async def test_get_student_attendance_invalid_user():
    result = await get_student_attendance(-999)
    assert result.get("success") is False
    assert "error" in result


@pytest.mark.anyio
async def test_get_child_attendance_allowed():
    mock_data = {
        "student_id": 1,
        "student_name": "Rahul Sharma",
        "total_classes": 10,
        "present": 10,
        "absent": 0,
        "attendance_percentage": 100.0,
    }
    with patch("app.tools.attendance.erp_client.get_child_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_data
        result = await get_child_attendance(1)
        assert result.get("success") is True
        assert result["student_name"] == "Rahul Sharma"


@pytest.mark.anyio
async def test_mark_attendance_success():
    mock_data = {"message": "Rahul Sharma marked present.", "attendance_id": 101}
    with patch("app.tools.attendance.erp_client.mark_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_data
        result = await mark_attendance(student_id=1, date="2026-08-17", status="present")
        assert result.get("success") is True
        assert result["status"] == "present"


@pytest.mark.anyio
async def test_mark_attendance_invalid_status():
    result = await mark_attendance(student_id=1, date="2026-08-17", status="late")
    assert result.get("success") is False
    assert "error" in result


@pytest.mark.anyio
async def test_get_overall_attendance():
    mock_data = {
        "total_students": 100,
        "total_records": 1000,
        "present": 950,
        "absent": 50,
        "overall_attendance_percentage": 95.0,
    }
    with patch("app.tools.attendance.erp_client.get_overall_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_data
        result = await get_overall_attendance()
        assert result.get("success") is True
        assert result["total_students"] == 100
        assert result["overall_attendance_percentage"] == 95.0
