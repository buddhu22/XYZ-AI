from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.user import UserResponse


class TeacherBase(BaseModel):
    employee_id: str
    subject: str


class TeacherCreate(TeacherBase):
    user_id: int


class TeacherResponse(TeacherBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TeacherDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    employee_id: str
    subject: str

    model_config = ConfigDict(from_attributes=True)
