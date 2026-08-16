# 🎓 XYZ AI — Human-Like AI School Assistant

An intelligent, human-like AI assistant for school ecosystems — serving **students**, **parents**, **teachers**, and **school management**. Built as a hackathon assessment project with a production-grade architecture.

> **Current Status: Phase 2 — Mock School ERP, Database & REST APIs**
>
> Phase 2 implements the PostgreSQL database, SQLAlchemy models, Alembic migrations, seed data, and REST APIs that simulate a School ERP system. The AI agent, authentication, voice, avatar, and other advanced features will be implemented in later phases.

---

## 📐 Architecture Overview

```
┌─────────────────────┐
│   Next.js Frontend  │  ← React + TypeScript + Tailwind CSS
│   (localhost:3000)   │
└────────┬────────────┘
         │ HTTP / REST
         ▼
┌─────────────────────┐
│   FastAPI Backend    │  ← Python + Pydantic + SQLAlchemy
│   (localhost:8000)   │
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│  DB    │ │ AI Agent     │  ← Phase 3+
│ (PgSQL)│ │ (LangGraph)  │
└────────┘ └──────┬───────┘
                  │
           ┌──────┴───────┐
           │ LLM Tools    │  ← Phase 3+ (will call these APIs)
           │ Mock ERP APIs│
           └──────────────┘
```

The backend and frontend are **fully independent** — they communicate over HTTP and can be deployed separately.

---

## 🛠 Tech Stack

| Layer          | Technology                                  |
| -------------- | ------------------------------------------- |
| Frontend       | Next.js, React, TypeScript, Tailwind CSS    |
| Backend        | Python, FastAPI, Pydantic, SQLAlchemy 2.0   |
| Database       | PostgreSQL 16 (Docker)                      |
| Migrations     | Alembic                                     |
| Testing        | Pytest, FastAPI TestClient                  |
| AI (Phase 3+)  | Google Gemini API, LangGraph                |
| Container      | Docker, Docker Compose                      |

---

## 📁 Folder Structure

```
xyz-ai/
│
├── frontend/                   # Next.js application
│   ├── app/                    # App Router pages & layouts
│   ├── components/             # React components
│   ├── lib/                    # Utilities
│   └── types/                  # TypeScript type definitions
│
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py             # App entry point (CORS, routes)
│   │   ├── core/
│   │   │   └── config.py       # Pydantic Settings (env management)
│   │   ├── api/
│   │   │   ├── router.py       # Central API router
│   │   │   ├── routes/
│   │   │   │   └── health.py   # GET /health endpoint
│   │   │   └── v1/
│   │   │       ├── students.py     # Student APIs
│   │   │       ├── parents.py      # Parent APIs
│   │   │       ├── teachers.py     # Teacher APIs
│   │   │       └── attendance.py   # Attendance APIs
│   │   ├── db/
│   │   │   ├── base.py         # SQLAlchemy DeclarativeBase
│   │   │   ├── session.py      # Engine, SessionLocal, get_db()
│   │   │   └── seed.py         # Repeatable seed data script
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py         # User + UserRole enum
│   │   │   ├── student.py      # Student profile
│   │   │   ├── parent.py       # Parent + ParentStudent junction
│   │   │   ├── teacher.py      # Teacher profile
│   │   │   └── attendance.py   # Attendance records
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   │   ├── user.py
│   │   │   ├── student.py
│   │   │   ├── parent.py
│   │   │   ├── teacher.py
│   │   │   └── attendance.py
│   │   ├── services/           # Business logic layer
│   │   │   ├── student_service.py
│   │   │   ├── parent_service.py
│   │   │   ├── teacher_service.py
│   │   │   └── attendance_service.py
│   │   ├── agents/             # AI agent integration (Phase 3+)
│   │   ├── tools/              # LLM tools (Phase 3+)
│   │   └── utils/              # Utility functions
│   ├── alembic/                # Database migrations
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
│
├── tests/
│   └── backend/
│       └── test_phase2_apis.py # 17 automated tests
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## 🗄️ Database Architecture

### Entity Relationship Diagram

```
User (id, name, email, role, created_at)
 │
 ├── Student (user_id FK → User)
 │     │
 │     ├── ParentStudent ←── Parent (user_id FK → User)
 │     │
 │     └── Attendance (student_id FK → Student, marked_by FK → User)
 │
 ├── Parent (user_id FK → User)
 │
 ├── Teacher (user_id FK → User)
 │
 └── Principal (no extra table; role = "principal" on User)
```

### Tables

| Table              | Key Fields                                           | Purpose                                      |
| ------------------ | ---------------------------------------------------- | -------------------------------------------- |
| `users`            | id, name, email, role, created_at                    | Central identity for all roles               |
| `students`         | id, user_id (FK), roll_number, class_name, section   | Student-specific academic details            |
| `parents`          | id, user_id (FK), phone                              | Parent contact info                          |
| `parent_students`  | id, parent_id (FK), student_id (FK)                  | Many-to-many parent ↔ child mapping          |
| `teachers`         | id, user_id (FK), employee_id, subject               | Teacher employment details                   |
| `attendance`       | id, student_id (FK), date, status, marked_by (FK)    | Daily attendance log with duplicate guard     |

### Key Constraints

- **`users.role`**: Restricted to `student`, `parent`, `teacher`, `principal` via PostgreSQL ENUM
- **`attendance (student_id, date)`**: UNIQUE constraint prevents duplicate attendance on the same day
- **`parent_students (parent_id, student_id)`**: UNIQUE constraint prevents duplicate parent-child links

---

## 📡 API Reference

All APIs are under **`/api/v1/`** prefix.

### Attendance APIs

| Method | Endpoint                              | Description                        | Tags       |
| ------ | ------------------------------------- | ---------------------------------- | ---------- |
| GET    | `/api/v1/attendance/student/{id}`     | Student attendance summary         | Attendance |
| GET    | `/api/v1/attendance/child/{id}`       | Child attendance summary (parents) | Attendance |
| POST   | `/api/v1/attendance/mark`             | Mark student attendance            | Attendance |
| GET    | `/api/v1/attendance/overall`          | School-wide attendance analytics   | Attendance |

### Student APIs

| Method | Endpoint                    | Description          | Tags     |
| ------ | --------------------------- | -------------------- | -------- |
| GET    | `/api/v1/students`          | List all students    | Students |
| GET    | `/api/v1/students/{id}`     | Get student profile  | Students |

### Parent APIs

| Method | Endpoint                    | Description                       | Tags    |
| ------ | --------------------------- | --------------------------------- | ------- |
| GET    | `/api/v1/parents/{id}`      | Get parent profile with children  | Parents |

### Teacher APIs

| Method | Endpoint                    | Description          | Tags     |
| ------ | --------------------------- | -------------------- | -------- |
| GET    | `/api/v1/teachers/{id}`     | Get teacher profile  | Teachers |

### Health

| Method | Endpoint   | Description        |
| ------ | ---------- | ------------------ |
| GET    | `/health`  | Backend health     |

---

## ✅ Prerequisites

- **Python** ≥ 3.11
- **Node.js** ≥ 18
- **Docker & Docker Compose** (for PostgreSQL)

---

## 🔐 Environment Variables

| Variable               | Description                        | Default                                                  |
| ---------------------- | ---------------------------------- | -------------------------------------------------------- |
| `DATABASE_URL`         | PostgreSQL connection string       | `postgresql://postgres:postgres@localhost:5433/xyz_ai`   |
| `GEMINI_API_KEY`       | Google Gemini API key (Phase 3+)   | —                                                        |
| `SECRET_KEY`           | App secret for signing (Phase 3+)  | —                                                        |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins (JSON list)   | `["http://localhost:3000"]`                               |
| `NEXT_PUBLIC_API_URL`  | Backend URL for frontend           | `http://localhost:8000`                                   |

---

## 🚀 How to Run Locally

### 1. Clone & Setup Environment Files

```bash
cp .env.example .env
cp .env backend/.env
cp frontend/.env.local.example frontend/.env.local
```

### 2. Start PostgreSQL (Docker)

```bash
docker-compose up -d postgres
```

This starts PostgreSQL on **host port 5433** (mapped to container port 5432) with database `xyz_ai`.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed the database with mock data
python -m app.db.seed

# Start FastAPI
uvicorn app.main:app --reload --port 8000
```

The backend will be running at **http://localhost:8000**.

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be running at **http://localhost:3000**.

---

## 📚 API Documentation (Swagger)

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Testing

```bash
cd backend
python -m pytest ../tests/backend/test_phase2_apis.py -v
```

### Test Coverage

| Test Class            | Tests | Description                                |
| --------------------- | ----- | ------------------------------------------ |
| TestStudentAttendance | 2     | Valid/invalid student attendance lookup     |
| TestMarkAttendance    | 5     | Valid mark, invalid status/student/teacher, duplicate |
| TestOverallAttendance | 2     | Summary with data and empty database       |
| TestParentChild       | 2     | Valid parent-child link, invalid parent     |
| TestStudentProfile    | 3     | List all, get by ID, nonexistent           |
| TestTeacherProfile    | 2     | Get by ID, nonexistent                     |
| TestChildAttendance   | 1     | Child attendance summary for parents       |
| **Total**             | **17**| All passing ✅                              |

---

## 📋 Example API Requests

### Get Student Attendance

```bash
curl http://localhost:8000/api/v1/attendance/student/1
```

Response:
```json
{
  "student_id": 1,
  "student_name": "Rahul Sharma",
  "total_classes": 5,
  "present": 3,
  "absent": 2,
  "attendance_percentage": 60.0
}
```

### Mark Attendance (Teacher)

```bash
curl -X POST http://localhost:8000/api/v1/attendance/mark \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "date": "2026-08-17", "status": "present", "marked_by": 2}'
```

Response:
```json
{
  "message": "Attendance marked successfully",
  "attendance_id": 51
}
```

### Get Overall Attendance (Principal)

```bash
curl http://localhost:8000/api/v1/attendance/overall
```

Response:
```json
{
  "total_students": 10,
  "total_records": 50,
  "present": 36,
  "absent": 14,
  "overall_attendance_percentage": 72.0
}
```

### Get Parent with Children

```bash
curl http://localhost:8000/api/v1/parents/1
```

Response:
```json
{
  "id": 1,
  "user_id": 5,
  "name": "Rajesh Sharma",
  "email": "rajesh.sharma@mail.com",
  "phone": "9876543210",
  "children": [
    {
      "id": 1,
      "roll_number": "STU001",
      "class_name": "Class 10",
      "section": "A",
      "name": "Rahul Sharma"
    }
  ]
}
```

---

## 🗄️ Database Commands Reference

```bash
# Run all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create a new migration
alembic revision --autogenerate -m "description"

# Check current migration
alembic current

# View migration history
alembic history

# Re-seed the database (safe to run multiple times)
python -m app.db.seed
```

---

## 🔮 How These APIs Become AI Agent Tools

In **Phase 3**, the AI Agent (powered by Google Gemini + LangGraph) will call these exact REST APIs as tools. For example:

| User Says                              | AI Agent Calls                              |
| -------------------------------------- | ------------------------------------------- |
| "What is my attendance?"               | `GET /api/v1/attendance/student/{id}`       |
| "How much attendance does my child have?" | `GET /api/v1/attendance/child/{id}`      |
| "Mark Rahul absent today"              | `POST /api/v1/attendance/mark`              |
| "What is the overall attendance?"      | `GET /api/v1/attendance/overall`            |

The AI Agent will not access the database directly — it will always go through these APIs, ensuring proper validation and business logic.

---

## ⚠️ What is NOT Implemented Yet

Phase 2 is strictly **Database + Mock School ERP + REST APIs**. The following are planned for future phases:

- ❌ AI Agent / LLM integration (Gemini, LangGraph, LangChain)
- ❌ Prompt engineering / conversation memory
- ❌ Chat interface
- ❌ JWT Authentication / RBAC
- ❌ Voice / Speech-to-Text / Text-to-Speech
- ❌ AI Avatar
- ❌ Multilingual support
- ❌ Human escalation
- ❌ Prompt injection protection
- ❌ Production deployment

---

## 🗺 Phase Roadmap

| Phase | Focus                                          | Status |
| ----- | ---------------------------------------------- | ------ |
| 1 ✅  | Foundation, architecture, connectivity         | Done   |
| 2 ✅  | Database, mock school ERP APIs, schemas, tests | Done   |
| 3     | AI agent (Gemini + LangGraph), chat interface  | Next   |
| 4     | Authentication, RBAC, role-specific personas   | —      |
| 5     | Voice interaction, AI avatar, multilingual     | —      |
| 6     | Human escalation, security, prompt protection  | —      |
| 7     | Production deployment, monitoring, scaling     | —      |

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.
