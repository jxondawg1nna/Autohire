# AutoHire API

The AutoHire API is a FastAPI application that powers core platform functionality including candidate onboarding, job management, search orchestration, and integrations.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables should be defined in `.env`; see `.env.example` for required keys.

## Key Components

- `app/core/config.py`: Application configuration using Pydantic settings.
- `app/routes/`: Modular API routers for platform domains.
- `app/services/`: Business logic and integrations (placeholders for future work).
- `app/models/`: SQLAlchemy models and schemas (to be implemented).
- `tests/`: Pytest suite covering API endpoints and services.

