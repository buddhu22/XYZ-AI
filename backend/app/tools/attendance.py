"""
XYZ AI Backend — Attendance Tools (Phase 4)

Application-level tools for attendance queries and operations.
Uses explicit Pydantic schemas for input validation and output serialization.

Architecture Flow:
    XYZ AI Tool -> ERP API Client (httpx) -> Phase 2 ERP FastAPI -> PostgreSQL
"""

from typing import Dict, Any, Optional
from datetime import date as date_type
import logging
from pydantic import ValidationError

from app.services.erp_client import erp_client, ERPClientError
from app.schemas.tools import (
    StudentAttendanceToolInput,
    ChildAttendanceToolInput,
    MarkAttendanceToolInput,
    StudentAttendanceToolOutput,
    MarkAttendanceToolOutput,
    OverallAttendanceToolOutput,
)

logger = logging.getLogger("app.tools.attendance")


async def get_student_attendance(student_id: int) -> Dict[str, Any]:
    """
    TOOL: Fetch attendance summary for a student.
    
    Args:
        student_id: Integer ID of the student.
    """
    try:
        validated = StudentAttendanceToolInput(student_id=student_id)
    except ValidationError as e:
        return StudentAttendanceToolOutput(success=False, error=str(e.errors()[0]["msg"])).model_dump()

    try:
        data = await erp_client.get_student_attendance(validated.student_id)
        return StudentAttendanceToolOutput(
            success=True,
            student_id=data.get("student_id", validated.student_id),
            student_name=data.get("student_name", "Student"),
            total_classes=data.get("total_classes", 0),
            present_days=data.get("present", 0),
            absent_days=data.get("absent", 0),
            attendance_percentage=data.get("attendance_percentage", 0.0),
        ).model_dump()
    except ERPClientError as e:
        logger.warning(f"get_student_attendance failed: {e.message}")
        return StudentAttendanceToolOutput(success=False, error=e.message).model_dump()
    except Exception as e:
        logger.error(f"Unexpected error in get_student_attendance: {e}")
        return StudentAttendanceToolOutput(success=False, error="Failed to retrieve student attendance.").model_dump()


async def get_child_attendance(student_id: int) -> Dict[str, Any]:
    """
    TOOL: Fetch child attendance summary for a parent.
    
    Args:
        student_id: Integer ID of the child student.
    """
    try:
        validated = ChildAttendanceToolInput(student_id=student_id)
    except ValidationError as e:
        return StudentAttendanceToolOutput(success=False, error=str(e.errors()[0]["msg"])).model_dump()

    try:
        data = await erp_client.get_child_attendance(validated.student_id)
        return StudentAttendanceToolOutput(
            success=True,
            student_id=data.get("student_id", validated.student_id),
            student_name=data.get("student_name", "Child"),
            total_classes=data.get("total_classes", 0),
            present_days=data.get("present", 0),
            absent_days=data.get("absent", 0),
            attendance_percentage=data.get("attendance_percentage", 0.0),
        ).model_dump()
    except ERPClientError as e:
        logger.warning(f"get_child_attendance failed: {e.message}")
        return StudentAttendanceToolOutput(success=False, error=e.message).model_dump()
    except Exception as e:
        logger.error(f"Unexpected error in get_child_attendance: {e}")
        return StudentAttendanceToolOutput(success=False, error="Failed to retrieve child attendance.").model_dump()


async def mark_attendance(
    student_id: int,
    date: str,
    status: str,
) -> Dict[str, Any]:
    """
    TOOL: Mark daily attendance for a student.
    
    Args:
        student_id: Integer ID of the student.
        date: Date string in ISO format (YYYY-MM-DD) or 'today'.
        status: Attendance status ('present' or 'absent').
    """
    try:
        validated = MarkAttendanceToolInput(student_id=student_id, date=date, status=status)
    except ValidationError as e:
        return MarkAttendanceToolOutput(success=False, error=str(e.errors()[0]["msg"])).model_dump()

    # Resolve date string
    if not validated.date or validated.date.lower().strip() == "today":
        resolved_date = str(date_type.today())
    else:
        try:
            resolved_date = str(date_type.fromisoformat(validated.date.strip()))
        except ValueError:
            return MarkAttendanceToolOutput(
                success=False, error=f"Invalid date format '{date}'. Must be YYYY-MM-DD or 'today'."
            ).model_dump()

    try:
        # Default teacher ID for mock context fallback
        teacher_id = 1
        res = await erp_client.mark_attendance(
            student_id=validated.student_id,
            date=resolved_date,
            status=validated.status,
            teacher_id=teacher_id,
        )
        return MarkAttendanceToolOutput(
            success=True,
            message=res.get("message", "Attendance marked successfully."),
            attendance_id=res.get("attendance_id"),
            student_id=validated.student_id,
            date=resolved_date,
            status=validated.status,
        ).model_dump()
    except ERPClientError as e:
        logger.warning(f"mark_attendance failed: {e.message}")
        return MarkAttendanceToolOutput(success=False, error=e.message).model_dump()
    except Exception as e:
        logger.error(f"Unexpected error in mark_attendance: {e}")
        return MarkAttendanceToolOutput(success=False, error="Failed to mark attendance.").model_dump()


async def get_overall_attendance() -> Dict[str, Any]:
    """
    TOOL: Fetch school-wide overall attendance summary for principal/management.
    """
    try:
        data = await erp_client.get_overall_attendance()
        return OverallAttendanceToolOutput(
            success=True,
            total_students=data.get("total_students", 0),
            total_records=data.get("total_records", 0),
            present_count=data.get("present", 0),
            absent_count=data.get("absent", 0),
            overall_attendance_percentage=data.get("overall_attendance_percentage", 0.0),
        ).model_dump()
    except ERPClientError as e:
        logger.warning(f"get_overall_attendance failed: {e.message}")
        return OverallAttendanceToolOutput(success=False, error=e.message).model_dump()
    except Exception as e:
        logger.error(f"Unexpected error in get_overall_attendance: {e}")
        return OverallAttendanceToolOutput(success=False, error="Failed to retrieve overall attendance metrics.").model_dump()


# Backward compatibility aliases for Phase 3 legacy test suite
tool_get_student_attendance = get_student_attendance
tool_get_child_attendance = get_child_attendance
tool_mark_student_attendance = mark_attendance
tool_get_overall_attendance = get_overall_attendance
