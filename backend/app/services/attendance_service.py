from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict, Any

from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate


def get_student_attendance_summary(db: Session, student_id: int) -> Dict[str, Any]:
    # Validate student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get attendance records
    records = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    total_classes = len(records)
    present = sum(1 for r in records if r.status == "present")
    absent = total_classes - present
    percentage = (present / total_classes * 100.0) if total_classes > 0 else 0.0

    return {
        "student_id": student.id,
        "student_name": student.user.name,
        "total_classes": total_classes,
        "present": present,
        "absent": absent,
        "attendance_percentage": round(percentage, 2)
    }


def get_child_attendance_summary(db: Session, student_id: int) -> Dict[str, Any]:
    # Phase 2: returns the same summary as student attendance
    # Separated function so that parent-child authorization check can be plugged in later
    return get_student_attendance_summary(db, student_id)


def mark_student_attendance(db: Session, schema: AttendanceCreate) -> Attendance:
    # 1. Validate student exists
    student = db.query(Student).filter(Student.id == schema.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 2. Validate teacher/user exists
    teacher = db.query(Teacher).filter(Teacher.user_id == schema.marked_by).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # 3. Prevent duplicate attendance records for the same student on the same date
    existing = db.query(Attendance).filter(
        Attendance.student_id == schema.student_id,
        Attendance.date == schema.date
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Attendance record already exists for this student on this date"
        )

    # 4. Create and save record
    db_attendance = Attendance(
        student_id=schema.student_id,
        date=schema.date,
        status=schema.status,
        marked_by=schema.marked_by
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


def get_overall_attendance_summary(db: Session) -> Dict[str, Any]:
    total_students = db.query(Student).count()
    total_records = db.query(Attendance).count()
    present = db.query(Attendance).filter(Attendance.status == "present").count()
    absent = total_records - present
    percentage = (present / total_records * 100.0) if total_records > 0 else 0.0

    return {
        "total_students": total_students,
        "total_records": total_records,
        "present": present,
        "absent": absent,
        "overall_attendance_percentage": round(percentage, 2)
    }
