# Monitoring & Observability Guide

## The Three Pillars

### 1. Logs (What happened?)

**Tool:** structlog → JSON → CloudWatch / Datadog / ELK

Every request and pipeline stage logs structured JSON:

```json
{
  "event": "processing_complete",
  "lead_id": "abc-123",
  "score": 78,
  "timestamp": "2026-06-09T12:00:00Z",
  "level": "info"
}
```

**Key log events to alert on:**
- `processing_failed` — AI pipeline failure
- `unhandled_exception` — API crash
- `website_fetch_failed` — Scraping issues (informational)
- `llm_call_completed` — Track token usage per call

### 2. Metrics (How much? How fast?)

**Tool:** Prometheus → Grafana

Built-in metrics at `/api/v1/metrics`:

| Metric | Type | Alert Threshold |
|--------|------|-----------------|
| `http_requests_total` | Counter | — |
| `http_request_duration_seconds` | Histogram | p95 > 2s |
| Celery queue depth | Gauge | > 100 tasks |
| Lead processing duration | Histogram | p95 > 60s |
| OpenAI token usage | Counter | > $X/day |
| Lead processing failure rate | Counter | > 5% |

### 3. Traces (Where did time go?)

**Tool:** OpenTelemetry (add at 10k+ users)

Trace a lead from `POST /leads` through all 5 agent stages.

## Health Checks

### API Health (`GET /api/v1/health`)

Returns status of database and Redis connections. Wire this to:
- Docker Compose `healthcheck`
- Load balancer health probe
- Uptime monitoring (Pingdom, Better Uptime)

### Celery Worker Health

```bash
# Check active workers
celery -A app.tasks.celery_app inspect active

# Check queue depth
celery -A app.tasks.celery_app inspect reserved
```

## Dashboards to Build

### Operations Dashboard
- API request rate and latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Celery queue depth and worker count
- Database connection pool usage

### Business Dashboard
- Leads created per hour/day
- Average lead score distribution
- Processing success/failure rate
- Time from lead creation to "ready" status
- OpenAI cost per lead

### AI Quality Dashboard
- Token usage per agent type
- Processing duration per stage
- Reprocess rate (indicates quality issues)
- Website scrape success rate

## Alerting Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| API down | Health check fails 3x | Critical | Page on-call |
| High error rate | 5xx > 1% for 5 min | Critical | Page on-call |
| Queue backlog | > 100 pending tasks | Warning | Scale workers |
| Slow processing | p95 > 60s for 15 min | Warning | Investigate |
| OpenAI cost spike | Daily cost > 2x average | Warning | Review usage |
| DB connections | Pool > 80% utilized | Warning | Scale or optimize |

## Error Tracking

Add Sentry for exception tracking:

```python
# In app/main.py (production)
import sentry_sdk
sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.app_env)
```

Sentry captures:
- Unhandled exceptions with stack traces
- Celery task failures
- Performance transactions (API endpoint timing)

## Runbook: Common Incidents

### "Leads stuck in 'researching' status"
1. Check Celery workers: `celery inspect active`
2. Check Redis: `redis-cli ping`
3. Check OpenAI status page
4. Restart workers: `docker compose restart worker`
5. Reprocess stuck leads: `POST /leads/{id}/reprocess`

### "High OpenAI costs"
1. Check token usage logs: filter by `llm_call_completed`
2. Identify leads with large website content
3. Reduce `max_chars` in website scraper
4. Consider caching company research for duplicate domains

### "API returning 500 errors"
1. Check logs for `unhandled_exception`
2. Check database connectivity
3. Check connection pool exhaustion
4. Roll back to previous Docker image if recent deploy
