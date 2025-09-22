# Operations Guide

This guide summarizes operational considerations for deploying and maintaining AutoHire.

## Configuration Management

- Environment variables are consumed by each service; example files reside in the respective app directories.
- Secrets should be stored using your orchestrator's secret manager (Docker secrets, Kubernetes secrets, HashiCorp Vault, etc.).
- Feature flags and taxonomy management are handled via the Admin Console or API endpoints.

## Deployment

1. Build container images using the GitHub Actions workflow or local `docker build` commands.
2. Push images to a container registry (GitHub Container Registry by default).
3. Update the deployment stack (Docker Compose or Kubernetes manifests) to pull the new images.
4. Run database migrations (`apps/api` provides Alembic migrations) and search reindex jobs.

## Monitoring & Alerting

- Prometheus scrapes metrics endpoints from API, workers, Postgres, Redis, Meilisearch, Qdrant, and system exporters.
- Grafana dashboards visualize API latency, worker queue depth, search throughput, scraping success rate, and auto-apply conversions.
- Loki centralizes logs with structured fields for correlation.
- Alertmanager rules trigger notifications for error spikes, queue backlogs, failed scrapes, and resource saturation.

## Backup & Disaster Recovery

- PostgreSQL: employ physical replication and periodic logical dumps (`pg_dump`).
- MinIO: enable versioning and replicate to secondary storage for redundancy.
- Redis: configure AOF persistence for queue durability.
- Configuration (Keycloak realms, Grafana dashboards, PostHog data) should be exported regularly.

## Security

- Rotate Keycloak admin credentials and API secrets on a scheduled basis.
- Enforce TLS termination at the ingress layer.
- Apply network policies restricting database and storage access to necessary services.
- Audit access logs via Loki and retain for compliance requirements.

## Troubleshooting Tips

| Symptom | Checks |
| --- | --- |
| API 5xx errors | Inspect FastAPI logs in Loki, review Prometheus latency panel |
| Slow search results | Verify Meilisearch/Qdrant health, ensure workers are indexing |
| Resume parsing failures | Check Celery queue backlog and OCR dependencies |
| Auto-apply not firing | Validate rule schedules, inspect worker logs, confirm job matches exist |
| ATS sync errors | Review OpenCATS connectivity, ensure schema migration ran successfully |

