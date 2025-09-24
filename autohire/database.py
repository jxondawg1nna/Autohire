"""Database helpers for the Autohire application."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

_DEFAULT_DB_NAME = "autohire.db"
_DB_PATH: Optional[Path] = None


def set_db_path(path: Path) -> None:
    """Override the database path used by the application.

    Tests can call this helper to operate on an isolated database. When no
    explicit path is provided the application stores data in a SQLite database
    located next to the package.
    """

    global _DB_PATH
    _DB_PATH = path


def get_db_path() -> Path:
    """Return the current database path, creating a default one if needed."""

    global _DB_PATH
    if _DB_PATH is None:
        package_dir = Path(__file__).resolve().parent
        _DB_PATH = package_dir / _DEFAULT_DB_NAME
    return _DB_PATH


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with a row factory configured.

    The helper applies a module-level lock to avoid concurrent writes from
    different threads while still keeping the implementation lightweight.
    """

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create all database tables if they do not exist."""

    schema = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        department TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        resume TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        applied_at TEXT NOT NULL,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
        FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        scheduled_at TEXT NOT NULL,
        interviewer TEXT NOT NULL,
        feedback TEXT,
        result TEXT,
        FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
    );
    """

    with get_connection() as conn:
        conn.executescript(schema)
