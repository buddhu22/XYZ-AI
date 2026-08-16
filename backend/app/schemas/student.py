from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.user import UserResponse


class StudentBase(BaseModel):
    roll_number: str
    class_name: str
    section: str


class StudentCreate(StudentBase):
    user_id: int


class StudentResponse(StudentBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class StudentDetailResponse(BaseModel):
    id: int
    roll_number: str
    class_name: str
    section: str
    user_id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class StudentAttendanceSummary(BaseModel):
    student_id: int
    student_name: str
    total_classes: int
    present: int
    absent: int
    attendance_percentage: float

    model_config = ConfigDict(from_attributes=True)
