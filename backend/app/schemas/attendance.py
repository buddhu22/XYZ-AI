from datetime import datetime, date
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Literal


class AttendanceBase(BaseModel):
    student_id: int
    date: date
    status: Literal["present", "absent"]
    marked_by: int


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceMarkResponse(BaseModel):
    message: str
    attendance_id: int


class OverallAttendanceSummary(BaseModel):
    total_students: int
    total_records: int
    present: int
    absent: int
    overall_attendance_percentage: float

    model_config = ConfigDict(from_attributes=True)
