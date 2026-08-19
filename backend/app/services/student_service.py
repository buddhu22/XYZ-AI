from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from app.models.student import Student
from app.models.user import User, UserRole


def get_student_by_id(db: Session, student_id: int) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def get_all_students(db: Session) -> List[Student]:
    return db.query(Student).all()


def search_student_by_name(db: Session, name: str) -> List[Student]:
    """Search for students by partial name match (case-insensitive). Returns ALL matches."""
    return (
        db.query(Student)
        .join(User, Student.user_id == User.id)
        .filter(User.name.ilike(f"%{name}%"))
        .all()
    )


