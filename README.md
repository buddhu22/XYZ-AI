# XYZ AI — Human-Like School AI Assistant

> **Version 1.0.0** ·  
> A multimodal, multilingual AI assistant for School ERP ecosystems, powered by Google Gemini.

---

## Architecture

```text
┌──────────────────────────────────────────────────────┐
│                  School ERP Ecosystem                │
│                                                      │
│  Student Portal ─┐                                   │
│  Parent Portal  ─┼──▶ Next.js Frontend (Port 3000)   │
│  Staff Portal   ─┘         │                         │
│                            ▼                         │
│              FastAPI AI Backend (Port 8000)           │
│              ┌─────────────────────────────┐         │
│              │ Intent Detection (Gemini)   │         │
│              │ Entity Extraction           │         │
│              │ Clarification Engine        │         │
│              │ RBAC + Ownership Gate       │         │
│              │ Tool Calling Orchestrator   │         │
│              │ Persona + Multilingual      │         │
│              │ STT / TTS Services          │         │
│              │ Human Escalation System     │         │
│              │ Gemini Retry (tenacity)     │         │
│              └──────────┬──────────────────┘         │
│                         │                            │
│              ERP Client (httpx) ──▶ PostgreSQL       │
└──────────────────────────────────────────────────────┘
```

## Directory Structure

```text
XYZ AI/
├── frontend/           # Next.js 16 + React + TypeScript + Tailwind
│   ├── app/            # Pages & layouts
│   ├── components/     # ChatAssistant, Avatar, Dashboard UI
│   └── lib/            # API client utilities
│
├── backend/            # FastAPI + Pydantic + SQLAlchemy
│   ├── app/
│   │   ├── ai/         # Gemini service, intent, entities, persona, clarification
│   │   ├── api/        # Health, v1 REST endpoints, chat pipeline
│   │   ├── core/       # Config (pydantic-settings)
│   │   ├── db/         # Session, base model, seed data
│   │   ├── models/     # User, Student, Parent, Teacher, Attendance, Escalation
│   │   ├── schemas/    # Pydantic request/response schemas
│   │   ├── security/   # User context, permissions, RBAC, ownership
│   │   ├── services/   # ERP client, STT, TTS, escalation service
│   │   ├── tools/      # Gemini function-calling tool implementations
│   │   └── utils/      # Error handling utilities
│   ├── alembic/        # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
│
├── tests/backend/      # 128+ automated tests (pytest)
├── docker-compose.yml  # PostgreSQL + Backend + Frontend
├── .env.example        # Environment template
└── README.md
```

## Tech Stack

| Layer        | Technology                                         |
|--------------|----------------------------------------------------|
| Frontend     | Next.js 16, React, TypeScript, Tailwind CSS        |
| Backend      | Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0  |
| Database     | PostgreSQL 16                                      |
| Migrations   | Alembic                                            |
| AI Engine    | Google Gemini (gemini-3.6-flash) via google-genai   |
| Speech       | STT (Gemini Audio), TTS (gTTS)                     |
| Retry Logic  | tenacity (exponential backoff, bounded retries)     |
| Testing      | pytest, anyio, unittest.mock                       |
| Deployment   | Docker Compose                                     |

## API Endpoints

| Method  | Endpoint                         | Description                         |
|---------|----------------------------------|-------------------------------------|
| GET     | `/`                              | Project info                        |
| GET     | `/health`                        | Health check                        |
| POST    | `/api/v1/chat`                   | Text chat pipeline                  |
| POST    | `/api/v1/chat/voice`             | Voice chat (STT → Pipeline → TTS)   |
| GET     | `/api/v1/students`               | List students                       |
| GET     | `/api/v1/students/{id}`          | Get student by ID                   |
| GET     | `/api/v1/parents/{id}`           | Get parent with children            |
| GET     | `/api/v1/teachers/{id}`          | Get teacher by ID                   |
| GET     | `/api/v1/attendance/{id}`        | Student attendance summary          |
| POST    | `/api/v1/attendance`             | Mark attendance                     |
| POST    | `/api/v1/escalations`            | Create escalation ticket            |
| GET     | `/api/v1/escalations`            | List escalation tickets             |
| PATCH   | `/api/v1/escalations/{id}`       | Update escalation status            |

## Security Model

- **Intent-Level RBAC**: Every detected intent is checked against `ROLE_PERMISSIONS` before processing.
- **Tool-Level RBAC**: Every Gemini tool call passes through `authorize_tool_execution()` in Python.
- **Ownership Gate**: Students can only access their own data; parents can only access linked children.
- **No LLM-trusted security**: Gemini prompts are NOT relied upon for authorization — all checks are in Python.
- **Config Validation**: `SECRET_KEY` and `GEMINI_API_KEY` produce warnings if left at insecure defaults.

## Human Escalation

When a user says "I want to talk to a human" or similar, the pipeline:
1. Detects `HUMAN_ESCALATION` intent via Gemini structured output
2. Creates an `OPEN` escalation ticket in the database
3. Returns a reassuring message with the ticket ID
4. Staff can manage tickets via `GET/PATCH /api/v1/escalations`

## Environment Configuration

Copy `.env.example` to `.env` and fill in real values:

| Variable               | Purpose                        | Default                     |
|------------------------|--------------------------------|-----------------------------|
| `DATABASE_URL`         | PostgreSQL connection string   | `postgresql://...localhost`  |
| `GEMINI_API_KEY`       | Google Gemini API key          | _(empty — required)_        |
| `GEMINI_MODEL`         | Gemini model name              | `gemini-3.6-flash`          |
| `SECRET_KEY`           | Application secret key         | _(must change in prod)_     |
| `ERP_BASE_URL`         | ERP backend URL                | `http://127.0.0.1:8000`     |
| `BACKEND_CORS_ORIGINS` | Allowed frontend origins       | `["http://localhost:3000"]`  |
| `LOG_LEVEL`            | Logging level                  | `INFO`                      |
| `DEBUG`                | Enable debug mode              | `false`                     |

## Run Locally

**1. Start PostgreSQL:**
```bash
docker-compose up -d postgres
```

**2. Set up and run the backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

**3. Set up and run the frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Run Tests

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest ..\tests\backend\ -v
```

Expected: **128 tests passed**.

## Deploy with Docker

```bash
cp .env.example .env
# Edit .env with real secrets
docker-compose up --build -d
```

## License

See [LICENSE](./LICENSE).
