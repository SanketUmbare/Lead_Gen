# Deployment Guide

## Environments

| Environment | Purpose | Infrastructure |
|-------------|---------|----------------|
| Local | Development | Docker Compose |
| Staging | Pre-production testing | Single VPS or Railway |
| Production | Live customers | AWS/GCP with managed services |

## Local Development

```bash
# Start infrastructure
docker compose up -d postgres redis

# Backend (with hot reload)
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Add OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000

# Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Seed admin user
python scripts/seed.py
```

## Staging Deployment

### Option A: Single VPS (DigitalOcean, Hetzner)

```bash
# On server
git clone <repo>
cd Lead_Gen
cp backend/.env.example backend/.env
# Edit .env with production values

docker compose -f docker-compose.yml up -d
docker compose exec api python scripts/seed.py
```

### Option B: Railway / Render

1. Connect GitHub repo
2. Set environment variables from `.env.example`
3. Deploy backend, worker, frontend as separate services
4. Add managed PostgreSQL and Redis

**Staging checklist:**
- [ ] `APP_ENV=staging`
- [ ] Strong `JWT_SECRET_KEY` (32+ random chars)
- [ ] Valid `OPENAI_API_KEY`
- [ ] CORS_ORIGINS set to staging frontend URL
- [ ] `DEBUG=false`

## Production Deployment

### Recommended Architecture (AWS)

```
Route 53 (DNS)
    → CloudFront (CDN for frontend)
    → ALB (Load Balancer)
        → ECS Fargate (API containers, auto-scaling)
        → ECS Fargate (Celery workers, auto-scaling)
    → RDS PostgreSQL (Multi-AZ)
    → ElastiCache Redis (Cluster mode)
    → Secrets Manager (API keys, JWT secret)
    → CloudWatch (Logs + Metrics + Alarms)
```

### Production Checklist

- [ ] `APP_ENV=production`
- [ ] `DEBUG=false`
- [ ] Secrets in AWS Secrets Manager / Vault (not .env files)
- [ ] RDS with automated backups (7-day retention minimum)
- [ ] Redis with persistence enabled
- [ ] HTTPS everywhere (TLS 1.2+)
- [ ] CORS restricted to production domain
- [ ] Rate limiting on API (add nginx or API gateway)
- [ ] Database connection pooling (PgBouncer at scale)
- [ ] Celery worker auto-scaling based on queue depth
- [ ] Health check endpoints wired to load balancer
- [ ] Sentry DSN configured for error tracking
- [ ] Log aggregation (CloudWatch / Datadog)
- [ ] Database migrations via Alembic (not `create_all`)

### Database Migrations

```bash
# Generate migration after model changes
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Docker Production Build

```bash
# Build images
docker build -t leadgen-api:latest ./backend
docker build -t leadgen-frontend:latest ./frontend

# Push to registry
docker tag leadgen-api:latest <ecr-url>/leadgen-api:latest
docker push <ecr-url>/leadgen-api:latest
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:

1. **Backend test** — Import check, lint against live Postgres + Redis
2. **Frontend build** — TypeScript compile + Next.js build
3. **Docker build** — Image build on `main` branch (deploy step added later)

### Adding Deployment

```yaml
# Add to ci.yml after docker-build job
deploy:
  needs: docker-build
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster leadgen --service api --force-new-deployment
```

## Rollback Strategy

1. **API/Frontend:** Deploy previous Docker image tag (< 2 min rollback)
2. **Database:** Alembic downgrade (test downgrades in staging first)
3. **Celery:** Workers pick up new code on restart; in-flight tasks complete with old code
