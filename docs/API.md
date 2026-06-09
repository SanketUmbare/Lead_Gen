# API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

## Authentication

All endpoints except `/auth/register`, `/auth/login`, and `/health` require a JWT token.

```
Authorization: Bearer <access_token>
```

### POST /auth/register

```json
{
  "email": "user@company.com",
  "password": "securepassword",
  "full_name": "Jane Smith"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@company.com",
  "full_name": "Jane Smith",
  "is_active": true
}
```

### POST /auth/login

```json
{
  "email": "user@company.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

## Leads

### POST /leads

Create a lead and queue AI processing.

```json
{
  "name": "John Doe",
  "email": "john@acme.com",
  "company": "Acme Corp",
  "role": "VP of Engineering",
  "website": "https://acme.com",
  "notes": "Found us via Google, interested in AI automation"
}
```

**Response (201):** Lead object with `status: "new"`.

The AI pipeline begins immediately via Celery. Poll `GET /leads/{id}` to track progress.

### GET /leads

List leads with pagination.

**Query params:** `page` (default 1), `page_size` (default 20, max 100)

**Response (200):**
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

### GET /leads/{id}

Full lead detail including all AI outputs.

**Response (200):**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "status": "ready",
  "company_research": {
    "company_summary": "...",
    "industry": "SaaS",
    "estimated_size": "50-200",
    "key_offerings": ["..."],
    "possible_pain_points": ["..."]
  },
  "lead_intelligence": {
    "probable_goals": ["..."],
    "probable_challenges": ["..."],
    "buying_authority": "decision_maker",
    "authority_score": 0.85
  },
  "lead_score": {
    "score": 78,
    "reasoning": "...",
    "factors": {
      "company_size": 20,
      "relevance": 22,
      "role_seniority": 21,
      "industry_fit": 15
    }
  },
  "outreach_messages": [
    {
      "message_type": "first_email",
      "subject": "...",
      "body": "..."
    }
  ],
  "ai_summary": {
    "lead_summary": "...",
    "opportunity_summary": "...",
    "recommended_action": "Schedule demo within 24h"
  },
  "activity_logs": [...]
}
```

### PATCH /leads/{id}

```json
{
  "status": "contacted",
  "notes": "Called on June 9, interested in demo"
}
```

### POST /leads/{id}/reprocess

Re-queue the full AI pipeline. Useful when processing failed or you want fresh output.

## Health & Monitoring

### GET /health

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy",
  "redis": "healthy",
  "timestamp": "2026-06-09T12:00:00Z"
}
```

### GET /metrics

Prometheus-format metrics endpoint.

## Lead Status Flow

```
new → researching → analyzed → ready → contacted → closed
                              ↘ failed (retry available)
```

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Validation error |
| 401 | Missing/invalid JWT |
| 404 | Resource not found |
| 500 | Internal server error |

```json
{
  "detail": "Error message"
}
```
