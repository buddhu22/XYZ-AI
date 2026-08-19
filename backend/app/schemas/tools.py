"""
XYZ AI Backend — Tool Input and Output Schemas

Defines explicit, strongly typed Pydantic schemas for AI tool inputs and results.
Guarantees clean input validation and prevents sensitive internal database properties from leaking.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# TOOL INPUT SCHEMAS
# =============================================================================

class StudentAttendanceToolInput(BaseModel):
    """Input parameters for fetching student attendance."""
    student_id: int = Field(..., gt=0, description="Positive integer ID of the student.")


class ChildAttendanceToolInput(BaseModel):
    """Input parameters for fetching child attendance."""
    student_id: int = Field(..., gt=0, description="Positive integer ID of the child student.")


class MarkAttendanceToolInput(BaseModel):
    """Input parameters for marking student attendance."""
    student_id: int = Field(..., gt=0, description="Positive integer ID of the student.")
    date: str = Field(..., description="Date string in YYYY-MM-DD format or 'today'.")
    status: Literal["present", "absent"] = Field(..., description="Attendance status: 'present' or 'absent'.")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        norm = v.lower().strip()
        if norm not in ("present", "absent"):
            raise ValueError("Status must be either 'present' or 'absent'.")
        return norm


# =============================================================================
# STRUCTURED TOOL OUTPUT SCHEMAS
# =============================================================================

class ToolOutputBase(BaseModel):
    """Base schema for structured tool execution results."""
    success: bool = Field(True, description="True if operation succeeded.")
    error: Optional[str] = Field(None, description="User-safe error message if operation failed.")


class StudentAttendanceToolOutput(ToolOutputBase):
    """Structured response for student attendance metrics."""
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    total_classes: int = 0
    present_days: int = 0
    absent_days: int = 0
    attendance_percentage: float = 0.0


class MarkAttendanceToolOutput(ToolOutputBase):
    """Structured response for marking attendance."""
    attendance_id: Optional[int] = None
    message: Optional[str] = None
    student_id: Optional[int] = None
    date: Optional[str] = None
    status: Optional[str] = None


class OverallAttendanceToolOutput(ToolOutputBase):
    """Structured response for school-wide attendance metrics."""
    total_students: int = 0
    total_records: int = 0
    present_count: int = 0
    absent_count: int = 0
    overall_attendance_percentage: float = 0.0
