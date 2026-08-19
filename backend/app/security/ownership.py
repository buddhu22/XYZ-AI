"""
XYZ AI Backend — Resource Ownership Verification

Verifies data access rights and database relationships (e.g., parent-child links)
before executing any data-retrieval tools.
"""

from typing import Optional, Union
from sqlalchemy.orm import Session
import logging

from app.models.user import User
from app.models.student import Student
from app.models.parent import Parent, ParentStudent

logger = logging.getLogger("app.security.ownership")


def verify_student_self_access(db: Session, student_user_id: int) -> Optional[Student]:
    """
    Retrieves the Student profile associated with the authenticated student's user ID.
    Returns None if no associated student profile is found.
    """
    student = db.query(Student).filter(Student.user_id == student_user_id).first()
    if not student:
        logger.warning(f"No student profile found for user_id={student_user_id}.")
        return None
    return student


def verify_parent_child_relationship(
    db: Session,
    parent_user_id: int,
    student_identifier: Optional[Union[str, int]] = None
) -> Optional[Student]:
    """
    Verifies that the requested student is actively linked to the authenticated parent in the database.
    
    :param db: SQLAlchemy Session.
    :param parent_user_id: The authenticated user's ID (must be a parent).
    :param student_identifier: Optional student name, student ID, or roll number.
                               If None and parent has exactly one child, returns that child.
    :return: The Student entity if verified and authorized, else None.
    """
    parent = db.query(Parent).filter(Parent.user_id == parent_user_id).first()
    if not parent:
        logger.warning(f"No parent profile found for user_id={parent_user_id}.")
        return None

    # Retrieve all children linked to this parent
    linked_students = (
        db.query(Student)
        .join(ParentStudent, ParentStudent.student_id == Student.id)
        .filter(ParentStudent.parent_id == parent.id)
        .all()
    )

    if not linked_students:
        logger.warning(f"Parent id={parent.id} has no linked students.")
        return None

    # If no identifier provided, and parent has only one child, return that child
    if not student_identifier:
        return linked_students[0] if len(linked_students) == 1 else None

    # If student_identifier is an integer or digit string (ID)
    if isinstance(student_identifier, int) or (isinstance(student_identifier, str) and student_identifier.isdigit()):
        target_id = int(student_identifier)
        for s in linked_students:
            if s.id == target_id or s.user_id == target_id:
                return s
        return None

    # If student_identifier is a string (Name or Roll Number)
    target_str = str(student_identifier).strip().lower()
    for s in linked_students:
        # Check student roll number
        if s.roll_number and s.roll_number.lower() == target_str:
            return s
        # Check student user name
        if s.user and s.user.name:
            user_name_lower = s.user.name.lower()
            if target_str == user_name_lower or target_str in user_name_lower.split():
                return s

    logger.warning(
        f"Parent id={parent.id} is NOT linked to student '{student_identifier}'."
    )
    return None
