"""
XYZ AI Backend — Resource Ownership Tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent, ParentStudent
from app.models.teacher import Teacher
from app.security.ownership import verify_student_self_access, verify_parent_child_relationship


# In-memory test DB
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seeded_db(db):
    # Create Parent
    parent_user = User(name="Rajesh Sharma", email="rajesh@mail.com", role=UserRole.PARENT)
    db.add(parent_user)
    db.commit()
    db.refresh(parent_user)
    parent = Parent(user_id=parent_user.id, phone="9876543210")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # Create Student 1 (Linked to Parent)
    student1_user = User(name="Rahul Sharma", email="rahul@mail.com", role=UserRole.STUDENT)
    db.add(student1_user)
    db.commit()
    db.refresh(student1_user)
    student1 = Student(user_id=student1_user.id, roll_number="STU001", class_name="Class 10", section="A")
    db.add(student1)
    db.commit()
    db.refresh(student1)

    # Link Parent and Student 1
    junction = ParentStudent(parent_id=parent.id, student_id=student1.id)
    db.add(junction)
    db.commit()

    # Create Student 2 (NOT linked to Parent)
    student2_user = User(name="Priya Verma", email="priya@mail.com", role=UserRole.STUDENT)
    db.add(student2_user)
    db.commit()
    db.refresh(student2_user)
    student2 = Student(user_id=student2_user.id, roll_number="STU002", class_name="Class 10", section="A")
    db.add(student2)
    db.commit()
    db.refresh(student2)

    return {
        "parent_user": parent_user,
        "student1_user": student1_user,
        "student2_user": student2_user,
        "student1": student1,
        "student2": student2,
    }


def test_student_self_access_valid(db, seeded_db):
    student_user_id = seeded_db["student1_user"].id
    student = verify_student_self_access(db, student_user_id)
    assert student is not None
    assert student.roll_number == "STU001"


def test_student_self_access_invalid_user(db, seeded_db):
    student = verify_student_self_access(db, 9999)
    assert student is None


def test_parent_child_relationship_allowed(db, seeded_db):
    parent_user_id = seeded_db["parent_user"].id
    
    # Access child by first name
    student_by_name = verify_parent_child_relationship(db, parent_user_id, "Rahul")
    assert student_by_name is not None
    assert student_by_name.roll_number == "STU001"
    
    # Access child by roll number
    student_by_roll = verify_parent_child_relationship(db, parent_user_id, "STU001")
    assert student_by_roll is not None
    assert student_by_roll.id == seeded_db["student1"].id


def test_parent_child_relationship_denied_unrelated(db, seeded_db):
    parent_user_id = seeded_db["parent_user"].id
    
    # Attempting to access unrelated student "Priya"
    student = verify_parent_child_relationship(db, parent_user_id, "Priya")
    assert student is None
