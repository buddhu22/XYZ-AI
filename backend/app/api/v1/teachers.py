from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.teacher import TeacherDetailResponse
from app.services import teacher_service

router = APIRouter()


@router.get("/{teacher_id}", response_model=TeacherDetailResponse, summary="Get teacher profile by ID")
def get_teacher_by_id(teacher_id: int, db: Session = Depends(get_db)):
    """Retrieve teacher metadata and core user profile information."""
    t = teacher_service.get_teacher_by_id(db, teacher_id)
    return TeacherDetailResponse(
        id=t.id,
        user_id=t.user_id,
        name=t.user.name,
        email=t.user.email,
        employee_id=t.employee_id,
        subject=t.subject
    )
