# Security Policy — Bluelink FastAPI Gateway

This document describes the security considerations and guidelines for running and extending the **Bluelink FastAPI Gateway**.

> ⚠️ Important: This project is a personal/portfolio backend and must be secured properly before any production use.

---

## Supported Versions

Security fixes are only guaranteed for the latest main branch of this repository.  
Older commits may contain outdated dependencies or vulnerable configurations.

---

## Secrets Management

The application uses environment variables (e.g. `.env`) to configure:

- `DATABASE_URL`
- Future: API keys for external Bluelink APIs
- Future: JWT signing keys

**Guidelines:**

- Never commit `.env` files or secrets into Git repositories.
- Use `.gitignore` to exclude local configuration files.
- In production, use:
  - Docker secrets
  - Environment variables managed by the hosting platform
  - A secrets manager (e.g. AWS Secrets Manager, Vault)

---

## Authentication & Authorization

Current state:

- The demo API does **not** implement authentication or authorization yet.
- All endpoints are open for demonstration purposes.

Before any production exposure on the Internet, you must:

1. Add proper authentication (e.g. OAuth2 / JWT).
2. Restrict access to internal endpoints (e.g. via API gateway, VPN or IP allow-list).
3. Validate that rate limiting and abuse protection are in place if exposed publicly.

---

## Transport Security (HTTPS/TLS)

For local development:

- HTTP (`http://localhost:8000`) is acceptable.

For any remote deployment:

- Use HTTPS termination (reverse proxy such as Traefik, Nginx or a cloud load balancer).
- Ensure TLS certificates are valid and auto-renewed (e.g. Let’s Encrypt).

The FastAPI application should normally run behind a reverse proxy rather than being exposed directly.

---

## Database Security

- Use separate PostgreSQL users and strong passwords.
- Restrict network access to the database (only from the application / internal network).
- Do not expose the database port (5432) to the public Internet.
- Use migrations (Alembic) instead of manual schema changes.

In Docker setups, prefer:

- An internal Docker network for app ↔ DB communication.
- No external port mapping for PostgreSQL in production.

---

## Dependencies

The project relies on Python dependencies listed in `requirements.txt`.

Recommendations:

- Regularly update dependencies to benefit from security fixes.
- Use tools like `pip-audit` or `safety` to scan for vulnerable packages.
- Pin dependency versions to avoid unexpected breaking changes.

Example:

```bash
pip install --upgrade pip
pip install pip-audit
pip-audit
```

---

## Logging & Monitoring

- Avoid logging sensitive data (access tokens, API keys, personal data).
- Log only what is necessary for debugging and observability.
- For production, integrate with:
  - Centralized logging (e.g. ELK, Loki)
  - Metrics (e.g. Prometheus + Grafana)
  - Alerting on errors and abnormal traffic patterns

---

## Reporting a Vulnerability

If you discover a vulnerability or security issue in this project:

- Do **not** open a public GitHub issue with sensitive details.
- Instead, contact the maintainer privately (e.g. via email or private message).

Provide as much detail as possible:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix if you have one

The maintainer will:

1. Acknowledge receipt.
2. Investigate the issue.
3. Prepare a fix and release a patch.
4. Optionally credit you if you wish.

---

## Hardening Checklist (Before Production)

If this gateway is ever deployed for real-world use:

- [ ] Use HTTPS everywhere
- [ ] Add authentication/authorization on all endpoints
- [ ] Rotate and protect all secrets (DB, tokens, keys)
- [ ] Restrict database access (network + credentials)
- [ ] Configure proper CORS policies
- [ ] Add rate limiting / basic DDoS protection
- [ ] Enable structured logging and monitoring
- [ ] Keep dependencies up to date
