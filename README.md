# AutoHire

AutoHire is an open-source, self-hosted hiring and job marketplace platform that combines candidate and employer experiences in a single mono-repo. This repository contains application code, infrastructure manifests, and documentation for running the full stack locally or in production.

## Repository Layout

- `apps/` — Source code for the Next.js front-ends, FastAPI backend, Celery workers, and supporting services.
- `infrastructure/` — Docker Compose, observability, and deployment configuration.
- `docs/` — Product and technical specifications, data models, and implementation plans.

## Getting Started

1. Review the product and system specification in [`docs/product-spec.md`](docs/product-spec.md) for an end-to-end overview of requirements.
2. Inspect [`infrastructure/docker-compose.yml`](infrastructure/docker-compose.yml) to understand the service topology required to run AutoHire locally.
3. Each application in `apps/` includes a `README.md` with development instructions and technology notes.

> **Note**: This repository currently provides the architecture skeleton and documentation necessary to build the platform. Functional implementations are intentionally minimal so that individual components can be developed iteratively.

## License

AutoHire is licensed under the MIT License. See [LICENSE](LICENSE) for details.
