# Infrastructure

This directory contains Docker Compose and observability configuration for running the AutoHire platform locally.

## Services

The default Compose stack provisions:

- Candidate, Employer, and Admin Next.js applications
- FastAPI backend (`api`) and Celery worker (`worker` + `scheduler`)
- PostgreSQL, Redis, MinIO, Meilisearch, Qdrant
- Keycloak for authentication, OpenCATS for ATS syncing
- MailHog for local email, PostHog for analytics
- Prometheus, Grafana, Loki, and Promtail for observability

## Usage

```bash
cd infrastructure
docker compose up --build
```

Each application consumes environment variables defined in its `.env.example`. Customize these values and copy them to `.env` files before running in production environments.

## Observability

- Prometheus configuration lives in `prometheus/prometheus.yml`.
- Grafana datasources and dashboards are pre-provisioned via `grafana/provisioning`.
- Loki and Promtail configuration is stored under `loki/`.

