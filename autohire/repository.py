"""Data access layer for the Autohire application."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Iterable, List, Optional

from fastapi import HTTPException, status

from . import models
from .database import get_connection

VALID_STATUSES = {"applied", "screening", "interview", "offer", "hired", "rejected"}


def _row_to_job(row) -> models.Job:
    return models.Job(id=row["id"], title=row["title"], description=row["description"], department=row["department"])


def _row_to_candidate(row) -> models.Candidate:
    return models.Candidate(id=row["id"], name=row["name"], email=row["email"], resume=row["resume"])


def _row_to_application(row) -> models.Application:
    return models.Application(
        id=row["id"],
        candidate_id=row["candidate_id"],
        job_id=row["job_id"],
        status=row["status"],
        applied_at=row["applied_at"],
    )


def _row_to_interview(row) -> models.Interview:
    return models.Interview(
        id=row["id"],
        application_id=row["application_id"],
        scheduled_at=datetime.fromisoformat(row["scheduled_at"]),
        interviewer=row["interviewer"],
        feedback=row["feedback"],
        result=row["result"],
    )


# Job operations -----------------------------------------------------------------

def create_job(data: models.JobCreate) -> models.Job:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO jobs (title, description, department) VALUES (?, ?, ?)",
            (data.title, data.description, data.department),
        )
        job_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _row_to_job(row)


def list_jobs() -> List[models.Job]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    return [_row_to_job(row) for row in rows]


def get_job(job_id: int) -> models.Job:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _row_to_job(row)


# Candidate operations ------------------------------------------------------------

def create_candidate(data: models.CandidateCreate) -> models.Candidate:
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO candidates (name, email, resume) VALUES (?, ?, ?)",
                (data.name, data.email, data.resume),
            )
        except sqlite3.IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate with this email already exists",
            ) from exc
        candidate_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
    return _row_to_candidate(row)


def list_candidates() -> List[models.Candidate]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM candidates ORDER BY id DESC").fetchall()
    return [_row_to_candidate(row) for row in rows]


def get_candidate(candidate_id: int) -> models.Candidate:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return _row_to_candidate(row)


# Application operations ----------------------------------------------------------

def _validate_application_references(candidate_id: int, job_id: int) -> None:
    with get_connection() as conn:
        candidate_exists = conn.execute("SELECT 1 FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
        job_exists = conn.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not candidate_exists or not job_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid candidate or job reference")


def create_application(data: models.ApplicationCreate) -> models.Application:
    _validate_application_references(data.candidate_id, data.job_id)

    applied_at = models.utcnow_iso()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications (candidate_id, job_id, status, applied_at)
            VALUES (?, ?, ?, ?)
            """,
            (data.candidate_id, data.job_id, "applied", applied_at),
        )
        application_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
    return _row_to_application(row)


def list_applications(status_filter: Optional[str] = None) -> List[models.Application]:
    query = "SELECT * FROM applications"
    params: Iterable[object] = []
    if status_filter:
        if status_filter not in VALID_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status filter")
        query += " WHERE status = ?"
        params = [status_filter]
    query += " ORDER BY applied_at DESC"

    with get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
    return [_row_to_application(row) for row in rows]


def get_application(application_id: int) -> models.Application:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return _row_to_application(row)


def update_application_status(application_id: int, status_update: models.ApplicationStatusUpdate) -> models.Application:
    new_status = status_update.status
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value")

    with get_connection() as conn:
        updated = conn.execute(
            "UPDATE applications SET status = ? WHERE id = ?",
            (new_status, application_id),
        )
        if updated.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
    return _row_to_application(row)


# Interview operations ------------------------------------------------------------

def create_interview(application_id: int, data: models.InterviewCreate) -> models.Interview:
    # Validate that the application exists before attempting to insert data.
    with get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM applications WHERE id = ?", (application_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

        cursor = conn.execute(
            """
            INSERT INTO interviews (application_id, scheduled_at, interviewer, feedback, result)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                application_id,
                data.scheduled_at.isoformat(),
                data.interviewer,
                data.feedback,
                data.result,
            ),
        )
        interview_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,)).fetchone()
    return _row_to_interview(row)


def list_interviews(application_id: int) -> List[models.Interview]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM interviews WHERE application_id = ? ORDER BY scheduled_at",
            (application_id,),
        ).fetchall()
    return [_row_to_interview(row) for row in rows]


# Reporting ----------------------------------------------------------------------

def get_pipeline_summary() -> dict:
    """Return aggregate metrics for the hiring pipeline."""

    with get_connection() as conn:
        totals = conn.execute(
            "SELECT status, COUNT(*) AS count FROM applications GROUP BY status"
        ).fetchall()
        total_candidates = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        total_jobs = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

    per_status = {row["status"]: row["count"] for row in totals}
    summary = {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "applications_per_status": per_status,
    }
    return summary
