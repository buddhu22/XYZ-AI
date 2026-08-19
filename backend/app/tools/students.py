"""
XYZ AI Backend — Student Lookup Tool

Provides a controlled student lookup utility to resolve student names
or IDs from the database. Used internally by the tools layer.
"""

from typing import Optional, Dict, Any
import logging

from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.user import User

logger = logging.getLogger("app.tools.students")


def tool_find_student_by_name(db: Session, student_name: str) -> Dict[str, Any]:
    """
    TOOL: Look up a student's basic profile by name (case-insensitive partial match).
    Returns structured info or an error if not found.
    """
    if not student_name or not student_name.strip():
        return {"error": "Student name is required for lookup."}

    student_user = (
        db.query(User)
        .filter(User.name.ilike(f"%{student_name.strip()}%"))
        .first()
    )

    if not student_user:
        return {"error": f"No student named '{student_name}' was found."}

    student = db.query(Student).filter(Student.user_id == student_user.id).first()
    if not student:
        return {"error": f"'{student_name}' does not have an active student profile."}

    return {
        "success": True,
        "student_id": student.id,
        "student_name": student_user.name,
        "roll_number": student.roll_number,
        "class_name": student.class_name,
        "section": student.section,
    }
