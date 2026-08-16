from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.user import UserResponse
from app.schemas.student import StudentDetailResponse


class ParentBase(BaseModel):
    phone: str


class ParentCreate(ParentBase):
    user_id: int


class ParentResponse(ParentBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ParentDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: str
    children: List[StudentDetailResponse]

    model_config = ConfigDict(from_attributes=True)
