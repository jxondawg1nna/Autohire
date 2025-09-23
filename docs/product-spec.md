# AutoHire Product & Technical Specification

This document captures the high-level goals, functional requirements, and system modules for the AutoHire platform. It is an adaptation of the collaboratively defined product vision and is intended to guide implementation across all teams.

## 0. Goals & Principles

**Goal:** Deliver a fully open-source, self-hosted, minimal-ops hiring and job-marketplace platform that provides candidate and employer portals, a microtask marketplace, resume tooling, hybrid search, ATS synchronization, observability, and CI/CD out of the box.

**Principles:**

- Prefer simplicity and minimal dependencies.
- Design modular services that can be deployed independently.
- Prioritize local-first data ownership and privacy-by-default configurations.
- Instrument every surface for observability and analytics.

## 1. Roles & Permissions

| Role | Capabilities |
| --- | --- |
| Anonymous | Browse public jobs/tasks, sign up |
| Candidate | Full candidate experience |
| Employer Recruiter | Post jobs/tasks, manage applicants |
| Org Admin | Manage organization settings and seats |
| System Admin | Platform configuration, moderation, observability |

## 2. Modules

- Candidate Portal (Next.js 14)
- Employer Portal (Next.js 14)
- Admin Console (Next.js 14)
- Ingestion & Processing (FastAPI + Celery)
- Search (Meilisearch + Qdrant)
- Storage (PostgreSQL + MinIO)
- ATS Bridge (OpenCATS)
- Scraping / Job Discovery (Playwright workers)
- Notifications (email + in-app)
- Analytics & Personalization (PostHog OSS)
- CI/CD (GitHub Actions)
- Observability (Prometheus + Grafana + Loki)

## 3. Open-Source Stack

All components are self-hostable and avoid external SaaS dependencies by default. Key services include Next.js, FastAPI, Celery, Redis, PostgreSQL, MinIO, Meilisearch, Qdrant, OpenCATS, Playwright, PostHog, Prometheus, Grafana, Loki, and Keycloak. Optional relays for email, maps, geocoding, or SMS can be integrated with documented setup steps when required.

## 4. Feature Matrix

### 4.1 Candidate Portal

- Sign up/auth via email+password and Keycloak OIDC
- Onboarding wizard collecting personal, professional, and preference data
- Profile editing with experiences, education, certifications, skills, links
- Resume management with parsing, improvement, and template export
- Job discovery combining list and map views with hybrid search and filters
- Microtask marketplace participation with submission workflows
- Auto-apply rules with scheduling, template selection, and logging
- Notifications (in-app + email), calendar availability, optional inbox

### 4.2 Employer Portal

- Organization and team management with roles/permissions
- Company profile setup
- Job authoring, enrichment, publishing, and applicant pipeline
- Microtask campaign creation, review, and payout workflows
- Candidate sourcing with hybrid search and saved lists
- Screening questionnaires and scheduling tools
- Offer generation via templates
- ATS synchronization toggles and logs

### 4.3 Admin Console

- User/org moderation and management
- Taxonomy (skills/roles) management
- Feature flags and configuration
- Observability dashboard aggregation
- Scraping source configuration

## 5. Forms & Field Definitions

Detailed field requirements are defined for candidate onboarding, profile editing, job filters, job postings, and microtask creation. Validation rules include format checks (e.g., RFC 5322 email, password complexity), file size/type limits, and structured enumerations for pay periods, work types, and language proficiency.

## 6. Data Model (PostgreSQL)

A relational schema covers users, candidates, employers, jobs, applications, microtasks, search indexes, embeddings, events, notifications, and auto-apply rules. See [`data-model.md`](data-model.md) for entity relationship diagrams and field descriptions.

## 7. ATS (OpenCATS) Mapping

Candidate, resume, job, and application records synchronize with OpenCATS using runtime schema introspection and version-checked migrations. Mapping covers candidate personal details, resumes as attachments, job order data, and pipeline statuses.

## 8. Hybrid Search Logic

Hybrid search blends Meilisearch keyword relevance with Qdrant semantic similarity using the all-MiniLM-L6-v2 embedding model. Results are re-ranked by freshness, compensation, location proximity, and personalization weights sourced from behavioral analytics.

## 9. Scraping & Job Discovery

Playwright-based workers execute scheduled scrapes across white-listed sources, respecting robots.txt and ToS. Extracted jobs are normalized, deduplicated, and indexed. Map rendering leverages Leaflet with OpenStreetMap tiles and lazy-loaded clusters.

## 10. Automation & CV Improvement

Celery workers execute auto-apply rules, generating applications via native submissions or email when allowed. Resume improvement uses rules-based text analysis with optional local LLM assistance, and outputs ATS-friendly PDFs.

## 11. API (FastAPI)

Key endpoints cover authentication, candidate profiles, resumes, auto-apply rules, job search and application, employer job management, microtasks, ingestion, search, and admin operations. Endpoint scaffolding lives in `apps/api`.

## 12. Frontend (Next.js App Router)

Each portal uses the App Router with routes for onboarding, profiles, jobs, tasks, messaging, organization management, sourcing, settings, and admin oversight.

## 13. Personalization & Analytics

Events are captured in PostgreSQL and mirrored to PostHog. Signals drive skill weighting, recommendation tweaks, and ranking adjustments. Opt-out and deletion flows uphold privacy requirements.

## 14. Notifications

In-app notifications persist in the database. Email delivery defaults to MailHog/Postfix for local use with optional relays documented for production.

## 15. CI/CD

GitHub Actions workflows perform linting, testing, and Docker image builds, with optional deployment pipelines that pull new images, apply migrations, and trigger reindexing.

## 16. Observability

Prometheus scrapes exporters from API, workers, PostgreSQL, Redis, and supporting services. Grafana dashboards track performance, queue health, and scraping outcomes. Loki aggregates structured logs with alerting on error and latency thresholds.

## 17. Security & Privacy

Keycloak issues short-lived JWTs with role claims. FastAPI enforces row-level authorization. Sensitive data can be encrypted at rest, and MinIO serves resumés via signed URLs. GDPR-style export/delete operations are supported.

## 18. External Login Audit

Default deployment requires only local service logins (Keycloak, Grafana, Meilisearch, MinIO, OpenCATS). Integrations with external SaaS providers are optional and documented where relevant.

## 19. Milestones & Acceptance

1. **M1:** Core skeleton operational via Docker Compose; key flows functional; observability accessible.
2. **M2:** Employer workflows including OpenCATS sync operational.
3. **M3:** Microtasks and map experiences delivered.
4. **M4:** Auto-apply engine and CV tooling functional.
5. **M5:** Observability dashboards and CI/CD pipelines green.

## 20. Implementation Notes

- Use text-first resume parsing with OCR fallback.
- Cache embeddings and limit text length to 2–3k characters.
- Start hybrid weighting with α = 0.5 and iterate via feature flags.
- Keep scrapers modular per site and respect rate limits.
- Optimize map rendering via clustering and viewport-based loading.
- Store original and normalized resume assets with metadata in MinIO.
- Seed tests with factories and include Playwright end-to-end coverage.

