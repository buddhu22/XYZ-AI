from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceMarkResponse,
    OverallAttendanceSummary
)
from app.schemas.student import StudentAttendanceSummary
from app.services import attendance_service

router = APIRouter()


@router.get("/student/{student_id}", response_model=StudentAttendanceSummary, summary="Get student attendance summary")
def get_student_attendance_summary(student_id: int, db: Session = Depends(get_db)):
    """Calculate and return attendance totals and percentages for a student."""
    summary = attendance_service.get_student_attendance_summary(db, student_id)
    return StudentAttendanceSummary(**summary)


@router.get("/child/{student_id}", response_model=StudentAttendanceSummary, summary="Get child attendance summary for parents")
def get_child_attendance_summary(student_id: int, db: Session = Depends(get_db)):
    """Calculate child attendance summary. Note: Authorization is deferred to a future phase."""
    summary = attendance_service.get_child_attendance_summary(db, student_id)
    return StudentAttendanceSummary(**summary)


@router.post("/mark", response_model=AttendanceMarkResponse, summary="Mark student attendance")
def mark_student_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark daily attendance for a student. Validates student and teacher existence and prevents duplicate marks."""
    record = attendance_service.mark_student_attendance(db, payload)
    return AttendanceMarkResponse(
        message="Attendance marked successfully",
        attendance_id=record.id
    )


@router.get("/overall", response_model=OverallAttendanceSummary, summary="Get overall school attendance summary")
def get_overall_attendance_summary(db: Session = Depends(get_db)):
    """Calculate and return school-wide attendance metrics and percentages."""
    summary = attendance_service.get_overall_attendance_summary(db)
    return OverallAttendanceSummary(**summary)
