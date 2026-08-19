"""
Unit test suite for Phase 4 Step 6 Tool Schemas & Input/Output Serialization
"""

import pytest
from pydantic import ValidationError
from app.schemas.tools import (
    MarkAttendanceToolInput,
    StudentAttendanceToolInput,
    StudentAttendanceToolOutput,
    MarkAttendanceToolOutput,
)


def test_mark_attendance_input_validation():
    valid = MarkAttendanceToolInput(student_id=1, date="2026-08-18", status="present")
    assert valid.status == "present"

    with pytest.raises(ValidationError):
        MarkAttendanceToolInput(student_id=1, date="2026-08-18", status="invalid_status")


def test_student_attendance_input_validation():
    valid = StudentAttendanceToolInput(student_id=5)
    assert valid.student_id == 5

    with pytest.raises(ValidationError):
        StudentAttendanceToolInput(student_id=-1)


def test_tool_output_schema_serialization():
    out = StudentAttendanceToolOutput(
        success=True,
        student_id=1,
        student_name="Aarav Sharma",
        total_classes=10,
        present_days=9,
        absent_days=1,
        attendance_percentage=90.0,
    )
    dump = out.model_dump()
    assert dump["success"] is True
    assert dump["student_name"] == "Aarav Sharma"
    assert dump["attendance_percentage"] == 90.0
    assert "password" not in dump
    assert "secret" not in dump
