# Security Checklist

## Authentication & Authorization

- [x] JWT-based authentication with configurable expiry
- [x] Password hashing with bcrypt
- [x] Bearer token required on all protected endpoints
- [x] User-scoped data access (leads filtered by `owner_id`)
- [ ] Refresh token rotation (add for production)
- [ ] Token revocation blocklist in Redis (add at scale)
- [ ] Multi-factor authentication (roadmap)
- [ ] OAuth2 / SSO for enterprise (roadmap)

## API Security

- [x] CORS restricted to configured origins
- [x] Input validation via Pydantic schemas
- [x] Global exception handler (no stack traces in production)
- [ ] Rate limiting per user/IP (add nginx or middleware)
- [ ] Request size limits
- [ ] API key authentication for webhook integrations (roadmap)

## Data Security

- [x] Passwords stored as bcrypt hashes (never plaintext)
- [x] Database credentials via environment variables
- [ ] Encrypt sensitive fields at rest (PII encryption)
- [ ] Database backups encrypted
- [ ] Audit log for data access (roadmap)
- [ ] GDPR data deletion endpoint (roadmap)

## Infrastructure Security

- [x] Docker containers run as non-root (add in production Dockerfile)
- [x] Health checks don't expose sensitive data
- [ ] HTTPS/TLS everywhere (production)
- [ ] Secrets in vault (not .env files in production)
- [ ] Network isolation (VPC, security groups)
- [ ] WAF on load balancer
- [ ] Regular dependency vulnerability scanning

## AI-Specific Security

- [x] OpenAI API key stored in environment (not code)
- [x] Website scraping with timeout and size limits
- [x] LLM prompts don't include other users' data
- [ ] Prompt injection protection (sanitize user notes before LLM)
- [ ] Output filtering (prevent PII leakage in generated emails)
- [ ] Token usage limits per user/tenant

## OWASP Top 10 Coverage

| Risk | Status | Mitigation |
|------|--------|------------|
| Injection | Protected | SQLAlchemy ORM, Pydantic validation |
| Broken Auth | Protected | JWT + bcrypt, scoped access |
| Sensitive Data Exposure | Partial | HTTPS needed in prod, encrypt at rest |
| XXE | N/A | No XML parsing |
| Broken Access Control | Protected | owner_id filtering on all queries |
| Security Misconfiguration | Partial | Disable debug/docs in production |
| XSS | Protected | React auto-escapes, no dangerouslySetInnerHTML |
| Insecure Deserialization | Protected | JSON only, Pydantic validation |
| Known Vulnerabilities | Partial | Add dependabot + pip-audit in CI |
| Insufficient Logging | Protected | Structured logging on all operations |

## Pre-Launch Security Audit

Before acquiring paying customers:

1. Run `pip-audit` and `npm audit` — fix critical vulnerabilities
2. Penetration test on staging environment
3. Review all environment variables — no secrets in code
4. Enable HTTPS with valid certificates
5. Set `DEBUG=false` and disable `/docs` in production
6. Configure rate limiting
7. Set up WAF rules (block common attack patterns)
8. Document incident response plan
9. Review OpenAI data processing agreement
10. Implement GDPR-compliant data deletion
