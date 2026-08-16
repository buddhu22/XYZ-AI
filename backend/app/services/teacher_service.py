from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.teacher import Teacher


def get_teacher_by_id(db: Session, teacher_id: int) -> Teacher:
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher
