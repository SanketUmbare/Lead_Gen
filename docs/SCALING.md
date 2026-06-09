# Scaling Guide

## Current Architecture Capacity

| Component | Current Config | Capacity |
|-----------|---------------|----------|
| API (1 instance) | 1 uvicorn worker | ~100 req/s |
| Celery (2 workers) | concurrency=2 | ~4 leads/min |
| PostgreSQL | Single instance | ~1000 concurrent connections |
| Redis | Single instance | ~10k ops/s |

**Estimated capacity:** ~50-100 active users, ~500 leads/day.

---

## Scaling to 10,000 Users

### What Changes

| Component | From | To | Why |
|-----------|------|-----|-----|
| API | 1 instance | 3-5 instances behind ALB | Handle concurrent dashboard users |
| Celery | 2 workers | 4-8 workers | ~30 leads/min throughput |
| PostgreSQL | Single | Primary + 1 read replica | Dashboard reads don't hit primary |
| Redis | Single | Redis with persistence | Queue reliability |
| Frontend | Single | Vercel / CloudFront CDN | Static asset caching |
| Auth | JWT only | JWT + Redis token blocklist | Revoke compromised tokens |

### Code Changes Needed

1. **Read replica routing** — Dashboard list queries go to replica
2. **Connection pooling** — Add PgBouncer (transaction mode)
3. **Caching** — Cache lead list for 30s in Redis
4. **Rate limiting** — 100 req/min per user on API
5. **OpenAI batching** — Queue similar requests to reduce API calls

### Cost Estimate (10k users)

| Service | Monthly Cost |
|---------|-------------|
| ECS Fargate (API + Workers) | $200-400 |
| RDS PostgreSQL (db.r6g.large) | $150-250 |
| ElastiCache Redis | $50-100 |
| OpenAI API (~5k leads/day) | $500-2000 |
| CloudFront + ALB | $50-100 |
| Monitoring (Datadog) | $100-200 |
| **Total** | **$1,050-3,050/mo** |

### Revenue at 10k Users

At $49/mo per seat with 20% conversion: 2,000 paying × $49 = **$98,000/mo**
Gross margin: ~97% (typical for AI SaaS before sales/marketing costs).

---

## Scaling to 100,000 Users

### Architecture Evolution

```
                    ┌─────────────┐
                    │  CloudFront  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │     ALB      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐
        │ API (5-10)│ │Workers │ │Scheduler │
        │ instances │ │(10-20) │ │ (Celery  │
        └─────┬─────┘ └───┬────┘ │  Beat)   │
              │            │     └──────────┘
        ┌─────▼────────────▼─────┐
        │      PgBouncer          │
        └─────┬──────────┬───────┘
              │          │
        ┌─────▼────┐ ┌───▼──────┐
        │ Primary  │ │ Replica  │
        │ Postgres │ │ (2-3)    │
        └──────────┘ └──────────┘
```

### Major Changes

1. **Multi-tenant isolation** — `tenant_id` on all tables, row-level security
2. **Dedicated worker pools** — Separate queues for research, scoring, outreach
3. **AI cost optimization:**
   - Cache company research by domain (70% of leads share domains)
   - Use GPT-4o-mini for scoring, GPT-4o only for outreach
   - Batch API for non-urgent processing
4. **Event-driven architecture** — Replace Celery chain with event bus (SQS/SNS)
5. **Database sharding** — Shard by `tenant_id` when single DB exceeds 500GB
6. **CDN for API** — Cache GET /leads responses at edge
7. **WebSocket updates** — Replace polling with real-time lead status

### Team Structure at 100k Users

| Role | Count | Focus |
|------|-------|-------|
| Backend engineers | 3-4 | API, workers, data pipeline |
| Frontend engineer | 1-2 | Dashboard, UX |
| ML/AI engineer | 1-2 | Prompt optimization, model selection |
| DevOps/SRE | 1-2 | Infrastructure, monitoring |
| Product manager | 1 | Feature prioritization |

### Cost Estimate (100k users)

| Service | Monthly Cost |
|---------|-------------|
| ECS/EKS cluster | $1,000-3,000 |
| RDS (Multi-AZ, large) | $500-1,500 |
| ElastiCache Cluster | $200-500 |
| OpenAI API (~50k leads/day) | $5,000-20,000 |
| S3 + CloudFront | $200-500 |
| Monitoring + Security | $500-1,000 |
| **Total** | **$7,400-26,500/mo** |

### Revenue at 100k Users

At $49/mo, 20% conversion: 20,000 paying × $49 = **$980,000/mo**

---

## Scaling Decision Framework

```
Is the bottleneck...
├── API response time? → Scale API instances
├── Lead processing slow? → Scale Celery workers
├── Dashboard slow? → Add read replica + caching
├── OpenAI costs too high? → Cache, model downgrade, batching
├── Database size? → Partition by date, archive old leads
└── Team can't ship? → Hire, don't over-engineer infra
```

**Rule:** Scale the bottleneck, not everything. Measure first, optimize second.
