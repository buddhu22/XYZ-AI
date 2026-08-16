import sys
import os
from datetime import date, timedelta

# Add parent directory to sys.path so app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent, ParentStudent
from app.models.teacher import Teacher
from app.models.attendance import Attendance


def seed_db():
    print("Connecting to the database...")
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        db.query(Attendance).delete()
        db.query(ParentStudent).delete()
        db.query(Student).delete()
        db.query(Parent).delete()
        db.query(Teacher).delete()
        db.query(User).delete()
        db.commit()
        print("Existing data cleared.")

        # 1. Create Principal
        print("Seeding Principal...")
        principal_user = User(
            name="Suresh Nair",
            email="suresh.nair@school.com",
            role=UserRole.PRINCIPAL
        )
        db.add(principal_user)
        db.commit()

        # 2. Create Teachers
        print("Seeding Teachers...")
        teachers_data = [
            {"name": "Amit Kumar", "email": "amit.kumar@school.com", "employee_id": "TCH001", "subject": "Mathematics"},
            {"name": "Neha Singh", "email": "neha.singh@school.com", "employee_id": "TCH002", "subject": "Science"},
            {"name": "Rajesh Iyer", "email": "rajesh.iyer@school.com", "employee_id": "TCH003", "subject": "English"}
        ]
        teachers = []
        for t in teachers_data:
            u = User(name=t["name"], email=t["email"], role=UserRole.TEACHER)
            db.add(u)
            db.commit()
            db.refresh(u)
            teacher_profile = Teacher(user_id=u.id, employee_id=t["employee_id"], subject=t["subject"])
            db.add(teacher_profile)
            teachers.append(u)
        db.commit()

        # 3. Create Parents
        print("Seeding Parents...")
        parents_data = [
            {"name": "Rajesh Sharma", "email": "rajesh.sharma@mail.com", "phone": "9876543210"},
            {"name": "Sunita Verma", "email": "sunita.verma@mail.com", "phone": "9876543211"},
            {"name": "Vikram Singh", "email": "vikram.singh@mail.com", "phone": "9876543212"},
            {"name": "Anita Gupta", "email": "anita.gupta@mail.com", "phone": "9876543213"},
            {"name": "Manoj Patel", "email": "manoj.patel@mail.com", "phone": "9876543214"}
        ]
        parents = []
        for p in parents_data:
            u = User(name=p["name"], email=p["email"], role=UserRole.PARENT)
            db.add(u)
            db.commit()
            db.refresh(u)
            parent_profile = Parent(user_id=u.id, phone=p["phone"])
            db.add(parent_profile)
            db.commit()
            db.refresh(parent_profile)
            parents.append(parent_profile)

        # 4. Create Students
        print("Seeding Students...")
        students_data = [
            {"name": "Rahul Sharma", "email": "rahul.sharma@mail.com", "roll_number": "STU001", "class_name": "Class 10", "section": "A", "parent_index": 0},
            {"name": "Priya Verma", "email": "priya.verma@mail.com", "roll_number": "STU002", "class_name": "Class 10", "section": "A", "parent_index": 1},
            {"name": "Aman Singh", "email": "aman.singh@mail.com", "roll_number": "STU003", "class_name": "Class 10", "section": "A", "parent_index": 2},
            {"name": "Ananya Gupta", "email": "ananya.gupta@mail.com", "roll_number": "STU004", "class_name": "Class 10", "section": "B", "parent_index": 3},
            {"name": "Rohan Patel", "email": "rohan.patel@mail.com", "roll_number": "STU005", "class_name": "Class 10", "section": "B", "parent_index": 4},
            {"name": "Sneha Sharma", "email": "sneha.sharma@mail.com", "roll_number": "STU006", "class_name": "Class 10", "section": "A", "parent_index": 0},
            {"name": "Kabir Verma", "email": "kabir.verma@mail.com", "roll_number": "STU007", "class_name": "Class 10", "section": "B", "parent_index": 1},
            {"name": "Diya Sen", "email": "diya.sen@mail.com", "roll_number": "STU008", "class_name": "Class 10", "section": "B", "parent_index": 3},
            {"name": "Aarav Mehta", "email": "aarav.mehta@mail.com", "roll_number": "STU009", "class_name": "Class 10", "section": "A", "parent_index": 0},
            {"name": "Ishaan Kapoor", "email": "ishaan.kapoor@mail.com", "roll_number": "STU010", "class_name": "Class 10", "section": "B", "parent_index": 2}
        ]
        students = []
        for s in students_data:
            u = User(name=s["name"], email=s["email"], role=UserRole.STUDENT)
            db.add(u)
            db.commit()
            db.refresh(u)
            student_profile = Student(user_id=u.id, roll_number=s["roll_number"], class_name=s["class_name"], section=s["section"])
            db.add(student_profile)
            db.commit()
            db.refresh(student_profile)
            students.append(student_profile)

            # Link parent and child via ParentStudent
            parent = parents[s["parent_index"]]
            junction = ParentStudent(parent_id=parent.id, student_id=student_profile.id)
            db.add(junction)
        db.commit()

        # 5. Create Attendance Records
        print("Seeding Attendance records...")
        # Seed for last 5 school days
        today = date(2026, 8, 16)
        dates = [today - timedelta(days=d) for d in range(5)]
        
        # We will make Amit Kumar (teachers[0]) mark for Class 10 A, and Neha Singh (teachers[1]) for Class 10 B
        # Present status pattern:
        # Student 0, 1, 2: mostly present
        # Student 3, 4, 5: present except one day
        # Student 6, 7, 8, 9: mixed
        for d in dates:
            for i, student in enumerate(students):
                # Pick teacher who marked
                teacher_user = teachers[0] if student.section == "A" else teachers[1]
                
                # Determine status
                if i % 3 == 0:
                    status = "absent" if d.day % 4 == 0 else "present"
                elif i % 2 == 0:
                    status = "present"
                else:
                    status = "absent" if d.day % 3 == 0 else "present"
                
                record = Attendance(
                    student_id=student.id,
                    date=d,
                    status=status,
                    marked_by=teacher_user.id
                )
                db.add(record)
        db.commit()

        print("Database seeded successfully!")
        
        # Print seeded counts
        print(f"Total Users: {db.query(User).count()}")
        print(f"Total Teachers: {db.query(Teacher).count()}")
        print(f"Total Parents: {db.query(Parent).count()}")
        print(f"Total Students: {db.query(Student).count()}")
        print(f"Total Attendance Records: {db.query(Attendance).count()}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
