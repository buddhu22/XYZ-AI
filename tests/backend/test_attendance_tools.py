"""
Unit test suite for Phase 4 Step 2 Attendance Tools
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


@pytest.mark.anyio
async def test_get_student_attendance_success():
    mock_response = {
        "student_id": 1,
        "student_name": "Aarav Sharma",
        "total_classes": 10,
        "present": 9,
        "absent": 1,
        "attendance_percentage": 90.0,
    }
    with patch("app.tools.attendance.erp_client.get_student_attendance", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await get_student_attendance(1)
        assert result["success"] is True
        assert result["student_id"] == 1
        assert result["attendance_percentage"] == 90.0


@pytest.mark.anyio
async def test_get_student_attendance_invalid_id():
    result = await get_student_attendance(-5)
    assert result.get("success") is False
    assert "error" in result


@pytest.mark.anyio
async def test_get_child_attendance_success():
    mock_response = {
        "student_id": 2,
        "student_name": "Priya Verma",
        "total_classes": 12,
        "present": 12,
        "absent": 0,
        "attendance_percentage": 100.0,
    }
    with patch("app.tools.attendance.erp_client.get_child_attendance", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await get_child_attendance(2)
        assert result["success"] is True
        assert result["attendance_percentage"] == 100.0


@pytest.mark.anyio
async def test_mark_attendance_success():
    mock_response = {"message": "Attendance marked successfully", "attendance_id": 42}
    with patch("app.tools.attendance.erp_client.mark_attendance", new_callable=AsyncMock) as mock_mark:
        mock_mark.return_value = mock_response
        result = await mark_attendance(student_id=1, date="2026-08-18", status="absent")
        assert result["success"] is True
        assert result["attendance_id"] == 42
        assert result["status"] == "absent"


@pytest.mark.anyio
async def test_mark_attendance_invalid_status():
    result = await mark_attendance(student_id=1, date="2026-08-18", status="late")
    assert result.get("success") is False
    assert "error" in result


@pytest.mark.anyio
async def test_mark_attendance_invalid_date():
    result = await mark_attendance(student_id=1, date="invalid-date-format", status="present")
    assert "error" in result
    assert "Invalid date format" in result["error"]


@pytest.mark.anyio
async def test_get_overall_attendance_success():
    mock_response = {
        "total_students": 500,
        "total_records": 5000,
        "present": 4750,
        "absent": 250,
        "overall_attendance_percentage": 95.0,
    }
    with patch("app.tools.attendance.erp_client.get_overall_attendance", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await get_overall_attendance()
        assert result["success"] is True
        assert result["total_students"] == 500
        assert result["overall_attendance_percentage"] == 95.0
