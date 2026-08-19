from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.student import StudentDetailResponse
from app.services import student_service

router = APIRouter()


@router.get("", response_model=List[StudentDetailResponse], summary="List all students")
def list_all_students(name: Optional[str] = Query(None, description="Search student by name"), db: Session = Depends(get_db)):
    """Retrieve all students, or filter by ALL name matches if ?name= is provided."""
    if name:
        students = student_service.search_student_by_name(db, name)
    else:
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


@router.get("/user/{user_id}", response_model=StudentDetailResponse, summary="Get student profile by User ID")
def get_student_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """Retrieve student profile by user ID."""
    from app.models.user import User
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found for this user")
    s = user.student
    return StudentDetailResponse(
        id=s.id,
        roll_number=s.roll_number,
        class_name=s.class_name,
        section=s.section,
        user_id=s.user_id,
        name=s.user.name,
        email=s.user.email
    )

