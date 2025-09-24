# Autohire

Autohire is a lightweight hiring pipeline API that lets teams create jobs, track
candidates, manage applications, and schedule interviews. The service is built
with [FastAPI](https://fastapi.tiangolo.com/) and persists data to a local
SQLite database.

## Features

* Create and list job postings.
* Register candidates with resume summaries.
* Submit applications and track their progress through standard pipeline
  stages (applied, screening, interview, offer, hired, rejected).
* Schedule interviews, capture feedback, and monitor hiring pipeline summary
  metrics.

## Getting started

### Installation

Create and activate a virtual environment, then install the requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the API server

```bash
uvicorn autohire.api:app --reload
```

The server listens on http://127.0.0.1:8000. FastAPI automatically exposes
interactive API docs at http://127.0.0.1:8000/docs.

### Running the test suite

```bash
pytest
```

The tests spin up the FastAPI application against a temporary SQLite database
so they do not modify your development data.

## Project layout

```
autohire/
├── api.py          # FastAPI routes
├── database.py     # SQLite helpers and schema management
├── main.py         # Command line entry point for running the server
├── models.py       # Pydantic request/response schemas
└── repository.py   # Data access functions used by the API
```
