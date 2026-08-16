from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.student import StudentDetailResponse
from app.services import student_service

router = APIRouter()


@router.get("", response_model=List[StudentDetailResponse], summary="List all students")
def list_all_students(db: Session = Depends(get_db)):
    """Retrieve all student profiles in the system."""
    students = student_service.get_all_students(db)
    return [
        StudentDetailResponse(
            id=s.id,
            roll_number=s.roll_number,
            class_name=s.class_name,
            section=s.section,
            user_id=s.user_id,
            name=s.user.name,
            email=s.user.email
        )
        for s in students
    ]


@router.get("/{student_id}", response_model=StudentDetailResponse, summary="Get student profile by ID")
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific student profile including user identity details."""
    s = student_service.get_student_by_id(db, student_id)
    return StudentDetailResponse(
        id=s.id,
        roll_number=s.roll_number,
        class_name=s.class_name,
        section=s.section,
        user_id=s.user_id,
        name=s.user.name,
        email=s.user.email
    )
