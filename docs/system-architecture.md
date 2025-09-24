# System Architecture

This document describes the service topology, deployment model, and technology choices for AutoHire.

## High-Level Architecture

AutoHire follows a service-oriented architecture with a mono-repository housing multiple deployable units. Core components include:

- **Frontends:** Three Next.js 14 applications (Candidate, Employer, Admin) sharing a design system and leveraging the App Router.
- **Backend API:** FastAPI application exposing REST endpoints and orchestrating business logic.
- **Background Workers:** Celery workers for resume parsing, scraping, auto-apply automation, and asynchronous notifications.
- **Search Layer:** Meilisearch for keyword search and Qdrant for semantic search embeddings.
- **Storage:** PostgreSQL for relational data, MinIO for file objects, and Redis for caching and task queues.
- **ATS Bridge:** Integration services syncing data to OpenCATS.
- **Observability:** Prometheus, Grafana, and Loki for metrics, dashboards, and logs.
- **Analytics:** PostHog OSS for event tracking and personalization.

## Deployment Topology

```mermaid
flowchart LR
    subgraph Frontend
        Candidate[Candidate Portal]
        Employer[Employer Portal]
        Admin[Admin Console]
    end

    subgraph Backend
        API[FastAPI]
        Worker[Celery Workers]
        Scheduler[Celery Beat]
    end

    subgraph Data
        Postgres[(PostgreSQL)]
        Redis[(Redis)]
        MinIO[(MinIO)]
        Meili[(Meilisearch)]
        Qdrant[(Qdrant)]
    end

    subgraph Integrations
        OpenCATS[OpenCATS]
        PostHog[PostHog]
        Prometheus[Prometheus]
        Grafana[Grafana]
        Loki[Loki]
        Keycloak[Keycloak]
    end

    Candidate -->|OIDC| Keycloak
    Employer -->|OIDC| Keycloak
    Admin -->|OIDC| Keycloak

    Candidate --> API
    Employer --> API
    Admin --> API

    API --> Postgres
    API --> Redis
    API --> MinIO
    API --> Meili
    API --> Qdrant
    API --> OpenCATS
    API --> PostHog

    Worker --> Redis
    Worker --> Postgres
    Worker --> MinIO
    Worker --> Meili
    Worker --> Qdrant
    Worker --> OpenCATS

    Prometheus --> API
    Prometheus --> Worker
    Prometheus --> Postgres
    Prometheus --> Redis
    Prometheus --> Meili
    Prometheus --> Qdrant

    Grafana --> Prometheus
    Grafana --> Loki
    Loki --> API
    Loki --> Worker
    Loki --> Frontend
```

## Service Responsibilities

### API Service

- Authentication middleware (Keycloak JWT validation)
- Candidate profile and resume management
- Employer job and microtask management
- Hybrid search orchestration
- Notifications and event logging
- Admin endpoints for moderation and configuration

### Worker Service

- Resume parsing and normalization
- Hybrid search indexing
- Auto-apply execution and logging
- Microtask submission evaluation
- Scraping pipelines (Playwright-driven)
- Analytics aggregation and personalization jobs

### Frontend Applications

- **Candidate Portal:** Onboarding, profile, job discovery, microtasks, automation, notifications.
- **Employer Portal:** Organization management, job pipelines, microtasks, sourcing, ATS sync.
- **Admin Console:** Platform oversight, taxonomies, feature flags, observability links.

## Security Considerations

- Use Keycloak for SSO and role-based access control
- Enforce HTTPS and secure headers
- MinIO presigned URLs for file access
- Encrypt sensitive fields in PostgreSQL where required
- Provide GDPR-compliant data export and deletion flows

## Scaling Strategy

- Deploy each component as a container with horizontal scaling via orchestration (Docker Compose for local, Kubernetes or Nomad for production)
- Use Redis clustering for queue resilience if load increases
- Partition Celery workers by queue (parse, search, automation, scraping)
- Adopt Postgres read replicas for heavy reporting workloads

## Local Development

- Docker Compose orchestrates the full stack with developer-friendly defaults
- MailHog or Mailpit handles email testing
- Seed scripts provide sample data for quick onboarding
- `.env` files configure secrets; example env templates stored alongside services

