"""
Phase 2 — Automated tests for Mock School ERP REST APIs.

Uses an in-memory SQLite database so tests are isolated from real data.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent, ParentStudent
from app.models.teacher import Teacher
from app.models.attendance import Attendance
from app.db.session import get_db
from app.main import app


# ----- Test DB Setup -----

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ----- Fixtures -----

@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seed_data(db):
    """Seed a minimal set of data for testing."""
    # Principal
    principal_user = User(name="Suresh Nair", email="suresh@school.com", role=UserRole.PRINCIPAL)
    db.add(principal_user)
    db.commit()

    # Teacher
    teacher_user = User(name="Amit Kumar", email="amit@school.com", role=UserRole.TEACHER)
    db.add(teacher_user)
    db.commit()
    db.refresh(teacher_user)
    teacher = Teacher(user_id=teacher_user.id, employee_id="TCH001", subject="Mathematics")
    db.add(teacher)
    db.commit()

    # Parent
    parent_user = User(name="Rajesh Sharma", email="rajesh@mail.com", role=UserRole.PARENT)
    db.add(parent_user)
    db.commit()
    db.refresh(parent_user)
    parent = Parent(user_id=parent_user.id, phone="9876543210")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # Student
    student_user = User(name="Rahul Sharma", email="rahul@mail.com", role=UserRole.STUDENT)
    db.add(student_user)
    db.commit()
    db.refresh(student_user)
    student = Student(user_id=student_user.id, roll_number="STU001", class_name="Class 10", section="A")
    db.add(student)
    db.commit()
    db.refresh(student)

    # Parent-child link
    link = ParentStudent(parent_id=parent.id, student_id=student.id)
    db.add(link)
    db.commit()

    # Attendance records (3 present, 1 absent)
    for i, (d, status) in enumerate([
        (date(2026, 8, 11), "present"),
        (date(2026, 8, 12), "present"),
        (date(2026, 8, 13), "absent"),
        (date(2026, 8, 14), "present"),
    ]):
        db.add(Attendance(student_id=student.id, date=d, status=status, marked_by=teacher_user.id))
    db.commit()

    return {
        "student_id": student.id,
        "teacher_user_id": teacher_user.id,
        "parent_id": parent.id,
        "teacher_id": teacher.id,
    }


# ===== Student Attendance Tests =====

class TestStudentAttendance:
    def test_valid_student_attendance(self, seed_data):
        r = client.get(f"/api/v1/attendance/student/{seed_data['student_id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["student_name"] == "Rahul Sharma"
        assert data["total_classes"] == 4
        assert data["present"] == 3
        assert data["absent"] == 1
        assert data["attendance_percentage"] == 75.0

    def test_invalid_student_404(self):
        r = client.get("/api/v1/attendance/student/999")
        assert r.status_code == 404
        assert r.json()["detail"] == "Student not found"


# ===== Mark Attendance Tests =====

class TestMarkAttendance:
    def test_mark_valid_attendance(self, seed_data):
        r = client.post("/api/v1/attendance/mark", json={
            "student_id": seed_data["student_id"],
            "date": "2026-08-15",
            "status": "present",
            "marked_by": seed_data["teacher_user_id"]
        })
        assert r.status_code == 200
        data = r.json()
        assert data["message"] == "Attendance marked successfully"
        assert "attendance_id" in data

    def test_mark_invalid_status_422(self, seed_data):
        r = client.post("/api/v1/attendance/mark", json={
            "student_id": seed_data["student_id"],
            "date": "2026-08-15",
            "status": "late",
            "marked_by": seed_data["teacher_user_id"]
        })
        assert r.status_code == 422

    def test_mark_invalid_student_404(self, seed_data):
        r = client.post("/api/v1/attendance/mark", json={
            "student_id": 999,
            "date": "2026-08-15",
            "status": "present",
            "marked_by": seed_data["teacher_user_id"]
        })
        assert r.status_code == 404
        assert r.json()["detail"] == "Student not found"

    def test_mark_invalid_teacher_404(self, seed_data):
        r = client.post("/api/v1/attendance/mark", json={
            "student_id": seed_data["student_id"],
            "date": "2026-08-15",
            "status": "present",
            "marked_by": 999
        })
        assert r.status_code == 404
        assert r.json()["detail"] == "Teacher not found"

    def test_mark_duplicate_409(self, seed_data):
        # Mark once
        client.post("/api/v1/attendance/mark", json={
            "student_id": seed_data["student_id"],
            "date": "2026-08-15",
            "status": "present",
            "marked_by": seed_data["teacher_user_id"]
        })
        # Mark again — same student, same date
        r = client.post("/api/v1/attendance/mark", json={
            "student_id": seed_data["student_id"],
            "date": "2026-08-15",
            "status": "absent",
            "marked_by": seed_data["teacher_user_id"]
        })
        assert r.status_code == 409
        assert "already exists" in r.json()["detail"]


# ===== Overall Attendance Tests =====

class TestOverallAttendance:
    def test_overall_attendance_summary(self, seed_data):
        r = client.get("/api/v1/attendance/overall")
        assert r.status_code == 200
        data = r.json()
        assert data["total_students"] == 1
        assert data["total_records"] == 4
        assert data["present"] == 3
        assert data["absent"] == 1
        assert data["overall_attendance_percentage"] == 75.0

    def test_overall_empty_database(self):
        r = client.get("/api/v1/attendance/overall")
        assert r.status_code == 200
        data = r.json()
        assert data["total_students"] == 0
        assert data["total_records"] == 0
        assert data["overall_attendance_percentage"] == 0.0


# ===== Parent-Child Tests =====

class TestParentChild:
    def test_valid_parent_with_children(self, seed_data):
        r = client.get(f"/api/v1/parents/{seed_data['parent_id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Rajesh Sharma"
        assert len(data["children"]) == 1
        assert data["children"][0]["name"] == "Rahul Sharma"

    def test_invalid_parent_404(self):
        r = client.get("/api/v1/parents/999")
        assert r.status_code == 404
        assert r.json()["detail"] == "Parent not found"


# ===== Student Profile Tests =====

class TestStudentProfile:
    def test_list_all_students(self, seed_data):
        r = client.get("/api/v1/students")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["name"] == "Rahul Sharma"
        assert data[0]["roll_number"] == "STU001"

    def test_get_student_by_id(self, seed_data):
        r = client.get(f"/api/v1/students/{seed_data['student_id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Rahul Sharma"

    def test_get_nonexistent_student_404(self):
        r = client.get("/api/v1/students/999")
        assert r.status_code == 404


# ===== Teacher Profile Tests =====

class TestTeacherProfile:
    def test_get_teacher_by_id(self, seed_data):
        r = client.get(f"/api/v1/teachers/{seed_data['teacher_id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Amit Kumar"
        assert data["subject"] == "Mathematics"

    def test_get_nonexistent_teacher_404(self):
        r = client.get("/api/v1/teachers/999")
        assert r.status_code == 404


# ===== Child Attendance (Parent endpoint) Tests =====

class TestChildAttendance:
    def test_child_attendance_summary(self, seed_data):
        r = client.get(f"/api/v1/attendance/child/{seed_data['student_id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["student_name"] == "Rahul Sharma"
        assert data["attendance_percentage"] == 75.0
