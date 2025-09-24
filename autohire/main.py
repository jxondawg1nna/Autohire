"""Command line entry point for running the Autohire API server."""
from __future__ import annotations

import uvicorn


def run() -> None:
    """Run the FastAPI development server."""

    uvicorn.run("autohire.api:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":  # pragma: no cover - manual execution only
    run()
