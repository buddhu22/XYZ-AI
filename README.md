<<<<<<< HEAD
# XYZ-AI
=======
# 🎓 XYZ AI — Human-Like AI School Assistant

An intelligent, human-like AI assistant for school ecosystems — serving **students**, **parents**, **teachers**, and **school management**. Built as a hackathon assessment project with a production-grade architecture.

> **Current Status: Phase 1 — Foundation & Architecture**
>
> The AI agent, authentication, voice, avatar, and other advanced features will be implemented in later phases. Phase 1 establishes the project skeleton, backend/frontend connectivity, and database wiring.

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
│   FastAPI Backend    │  ← Python + Pydantic
│   (localhost:8000)   │
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│  DB    │ │ AI Agent     │  ← Phase 2+
│ (PgSQL)│ │ (LangGraph)  │
└────────┘ └──────┬───────┘
                  │
           ┌──────┴───────┐
           │ LLM Tools    │  ← Phase 2+
           │ Mock ERP APIs│
           └──────────────┘
```

The backend and frontend are **fully independent** — they communicate over HTTP and can be deployed separately.

---

## 🛠 Tech Stack

| Layer      | Technology                                  |
| ---------- | ------------------------------------------- |
| Frontend   | Next.js, React, TypeScript, Tailwind CSS    |
| Backend    | Python, FastAPI, Pydantic                   |
| Database   | PostgreSQL, SQLAlchemy 2.0                  |
| AI (Phase 2+) | Google Gemini API, LangGraph            |
| Container  | Docker, Docker Compose                      |

---

## 📁 Folder Structure

```
xyz-ai/
│
├── frontend/                   # Next.js application
│   ├── app/                    # App Router pages & layouts
│   │   ├── layout.tsx          # Root layout (SEO, fonts, theme)
│   │   ├── page.tsx            # Landing/dashboard page
│   │   └── globals.css         # Global styles & Tailwind config
│   ├── components/             # React components
│   │   ├── HealthStatus.tsx    # Backend connectivity indicator
│   │   └── RoleCard.tsx        # Role placeholder card
│   ├── lib/                    # Utilities
│   │   └── api.ts              # API client for backend communication
│   ├── types/                  # TypeScript type definitions
│   │   └── api.ts              # API response interfaces
│   ├── public/                 # Static assets
│   ├── .env.local.example      # Frontend env template
│   └── package.json
│
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py             # App entry point (CORS, routes)
│   │   ├── core/
│   │   │   └── config.py       # Pydantic Settings (env management)
│   │   ├── api/
│   │   │   ├── router.py       # Central API router
│   │   │   └── routes/
│   │   │       └── health.py   # GET /health endpoint
│   │   ├── db/
│   │   │   ├── base.py         # SQLAlchemy DeclarativeBase
│   │   │   └── session.py      # Engine, SessionLocal, get_db()
│   │   ├── models/             # DB models (Phase 2+)
│   │   ├── schemas/            # Pydantic schemas (Phase 2+)
│   │   ├── services/           # Business logic (Phase 2+)
│   │   ├── agents/             # AI agent integration (Phase 2+)
│   │   ├── tools/              # LLM tools (Phase 2+)
│   │   └── utils/              # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
│
├── tests/
│   ├── backend/                # Backend tests (Phase 2+)
│   └── frontend/               # Frontend tests (Phase 2+)
│
├── .env.example                # Root env template
├── .gitignore
├── docker-compose.yml          # PostgreSQL + Backend containers
├── README.md
└── LICENSE
```

---

## ✅ Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.11
- **PostgreSQL** ≥ 14 (or Docker)
- **Docker & Docker Compose** (optional, for containerized setup)

---

## 🔐 Environment Variables

| Variable               | Description                        | Default                                           |
| ---------------------- | ---------------------------------- | ------------------------------------------------- |
| `DATABASE_URL`         | PostgreSQL connection string       | `postgresql://postgres:postgres@localhost:5432/xyz_ai` |
| `GEMINI_API_KEY`       | Google Gemini API key (Phase 2+)   | —                                                 |
| `SECRET_KEY`           | App secret for signing (Phase 2+)  | —                                                 |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins (JSON list)   | `["http://localhost:3000"]`                        |
| `NEXT_PUBLIC_API_URL`  | Backend URL for frontend           | `http://localhost:8000`                            |

---

## 🚀 How to Run Locally

### 1. Clone & Setup Environment Files

```bash
# Copy environment templates
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

Edit `.env` with your actual values if needed.

---

### 2. PostgreSQL Setup

**Option A: Docker (Recommended)**

```bash
docker-compose up -d postgres
```

This starts PostgreSQL on port `5432` with database `xyz_ai`.

**Option B: Local PostgreSQL**

```sql
-- Connect to PostgreSQL and create the database
CREATE DATABASE xyz_ai;
```

Ensure your `DATABASE_URL` in `.env` matches your local PostgreSQL credentials.

---

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend (from the backend/ directory)
uvicorn app.main:app --reload --port 8000
```

The backend will be running at **http://localhost:8000**.

---

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be running at **http://localhost:3000**.

---

### 5. Docker Setup (Alternative — runs everything)

```bash
# Start PostgreSQL + Backend together
docker-compose up -d

# Frontend still runs natively
cd frontend && npm run dev
```

---

## ✅ How to Verify

### Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "xyz-ai-backend",
  "version": "0.1.0"
}
```

### Test Root Endpoint

```bash
curl http://localhost:8000/
```

### Test Frontend ↔ Backend Connectivity

1. Start the backend (`uvicorn app.main:app --reload`)
2. Start the frontend (`npm run dev`)
3. Open **http://localhost:3000**
4. Look at the header — you should see:
   - ✅ **"Backend Connected"** (green) — if the backend is running
   - ❌ **"Backend Disconnected"** (red) — if the backend is stopped

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ⚠️ Phase 1 Limitations

Phase 1 is **only** the project foundation. The following are **NOT** implemented yet:

- ❌ AI Agent / LLM integration
- ❌ LangGraph workflow
- ❌ Chat interface / conversation memory
- ❌ Authentication / JWT
- ❌ Role-Based Access Control (RBAC)
- ❌ Database models (Student, Teacher, Attendance, etc.)
- ❌ Mock School ERP APIs
- ❌ Voice / Speech-to-Text / Text-to-Speech
- ❌ AI Avatar
- ❌ Multilingual support
- ❌ Human escalation
- ❌ Prompt injection protection
- ❌ Production deployment

---

## 🗺 Future Phases

| Phase | Focus                                          |
| ----- | ---------------------------------------------- |
| 1 ✅  | Foundation, architecture, connectivity         |
| 2     | Database models, mock school APIs, schemas     |
| 3     | AI agent (Gemini + LangGraph), chat interface  |
| 4     | Authentication, RBAC, role-specific personas   |
| 5     | Voice interaction, AI avatar, multilingual     |
| 6     | Human escalation, security, prompt protection  |
| 7     | Production deployment, monitoring, scaling     |

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.
>>>>>>> 1c410e6 (feat: initial Phase 1 foundation & architecture for XYZ AI)
