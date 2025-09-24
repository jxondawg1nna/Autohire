"""Pydantic models used by the Autohire API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


def utcnow_iso() -> str:
    """Return the current UTC time formatted using ISO 8601."""

    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class JobBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int


class CandidateBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    resume: str = Field(..., min_length=1)


class CandidateCreate(CandidateBase):
    pass


class Candidate(CandidateBase):
    id: int


class ApplicationBase(BaseModel):
    candidate_id: int
    job_id: int


class ApplicationCreate(ApplicationBase):
    pass


class Application(ApplicationBase):
    id: int
    status: str
    applied_at: str


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., regex=r"^(applied|screening|interview|offer|hired|rejected)$")


class InterviewBase(BaseModel):
    scheduled_at: datetime
    interviewer: str = Field(..., min_length=1)
    feedback: Optional[str] = None
    result: Optional[str] = Field(default=None, regex=r"^(pass|fail|pending)$")


class InterviewCreate(InterviewBase):
    pass


class Interview(InterviewBase):
    id: int
    application_id: int


class InterviewSummary(BaseModel):
    interviewer: str
    scheduled_at: datetime
    result: Optional[str] = None
