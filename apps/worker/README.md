# Worker Service

The worker service executes asynchronous workloads such as resume parsing, hybrid search indexing, auto-apply automation, scraping, and notification dispatch.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
celery -A app.worker worker -l info
```

Environment variables follow `.env.example` and mirror the API configuration for shared resources.

## Planned Queues

- `parse`: resume ingestion and normalization.
- `search`: index maintenance for Meilisearch and Qdrant.
- `automation`: auto-apply execution and logging.
- `scrape`: scheduled job discovery tasks.

