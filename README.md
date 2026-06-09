# LeadGen AI — AI Lead Response System

Production-grade AI SaaS that automatically researches inbound leads, scores them, and generates personalized outreach.

## Quick Start (Local Development)

```bash
# 1. Clone and configure
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Add your OPENAI_API_KEY to backend/.env

# 2. Start all services
docker compose up -d

# 3. Seed admin user
docker compose exec api python scripts/seed.py

# 4. Open the app
# Frontend: http://localhost:3000
# API docs:  http://localhost:8000/docs
# Login:     admin@leadgen.ai / admin12345
```

## Project Structure

```
Lead_Gen/
├── backend/                 # FastAPI + Celery + SQLAlchemy
│   ├── app/
│   │   ├── api/             # HTTP routes (thin layer)
│   │   ├── agents/          # AI agents (company research, scoring, etc.)
│   │   ├── core/            # Config, security, logging
│   │   ├── db/              # Models + repositories
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── services/        # Business logic orchestration
│   │   └── tasks/           # Celery background jobs
│   ├── alembic/             # Database migrations
│   ├── scripts/             # Seed scripts
│   └── Dockerfile
├── frontend/                # Next.js 14 + TypeScript + Tailwind
│   └── src/
│       ├── app/             # Pages (App Router)
│       ├── components/      # UI components
│       └── lib/             # API client
├── docs/                    # Architecture, deployment, scaling guides
├── docker-compose.yml
└── .github/workflows/       # CI/CD pipeline
```

## Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│  Next.js │────▶│  FastAPI  │────▶│  PostgreSQL  │
│ Frontend │     │   API     │     │   Database   │
└──────────┘     └─────┬────┘     └──────────────┘
                       │
                       ▼
                 ┌──────────┐     ┌──────────────┐
                 │  Redis   │────▶│   Celery     │
                 │  Queue   │     │   Workers    │
                 └──────────┘     └──────┬───────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │  OpenAI API  │
                                  └──────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/leads` | Create lead (triggers AI pipeline) |
| GET | `/api/v1/leads` | List leads (paginated) |
| GET | `/api/v1/leads/{id}` | Lead detail with all AI outputs |
| PATCH | `/api/v1/leads/{id}` | Update lead status/notes |
| POST | `/api/v1/leads/{id}/reprocess` | Re-run AI pipeline |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/metrics` | Prometheus metrics |

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Monitoring Guide](docs/MONITORING.md)
- [Scaling Guide](docs/SCALING.md)
- [Security Checklist](docs/SECURITY.md)
- [Future Roadmap](docs/ROADMAP.md)

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14, TypeScript, Tailwind | SSR, type safety, rapid UI |
| API | FastAPI, Python 3.12 | Async, auto-docs, AI ecosystem |
| Database | PostgreSQL 16 | ACID, JSONB for AI outputs |
| ORM | SQLAlchemy 2.0 | Mature, migration support |
| Queue | Redis + Celery | Battle-tested async processing |
| AI | OpenAI GPT-4o-mini | Cost-effective, JSON mode |
| Auth | JWT | Stateless, horizontally scalable |
| Deploy | Docker Compose | Local dev = production parity |
