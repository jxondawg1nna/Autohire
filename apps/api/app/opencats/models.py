"""Pydantic models for OpenCATS synchronization."""

from __future__ import annotations

import base64
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, EmailStr, Field, model_validator


class WorkType(str, Enum):
    """Supported work type categories."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    OTHER = "other"


class ApplicationStatus(str, Enum):
    """Pipeline stages tracked for applications."""

    NEW = "new"
    SCREEN = "screen"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"


class LocalResume(BaseModel):
    """Representation of a candidate resume stored within AutoHire."""

    id: str
    candidate_id: str
    file_name: str
    content_type: str
    data: bytes

    def as_base64(self) -> str:
        """Return the resume payload encoded as base64 for transport."""

        return base64.b64encode(self.data).decode("ascii")


class LocalCandidate(BaseModel):
    """Subset of the candidate profile required for OpenCATS."""

    id: str
    employer_id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    city: str | None = None
    country: str | None = None
    summary: str | None = None
    desired_pay_min: int | None = Field(default=None, description="Stored in cents")
    desired_pay_max: int | None = Field(default=None, description="Stored in cents")
    work_type: WorkType | None = None
    availability: str | None = None
    skills: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class LocalJob(BaseModel):
    """Job definition synchronized to OpenCATS."""

    id: str
    employer_id: str
    title: str
    description: str
    city: str | None = None
    country: str | None = None
    salary_min: int | None = Field(default=None, description="Stored in cents")
    salary_max: int | None = Field(default=None, description="Stored in cents")
    work_type: WorkType | None = None
    external_id: str | None = None
    created_at: datetime
    updated_at: datetime


class LocalApplication(BaseModel):
    """Job application details required for synchronization."""

    id: str
    employer_id: str
    candidate_id: str
    job_id: str
    status: ApplicationStatus
    source: str | None = None
    resume_id: str | None = None
    submitted_at: datetime
    updated_at: datetime


class LocalApplicationBundle(BaseModel):
    """Combination of application, candidate and job data for mapping."""

    application: LocalApplication
    candidate: LocalCandidate
    job: LocalJob
    resume: LocalResume | None = None

    @model_validator(mode="after")
    def validate_relationships(self) -> "LocalApplicationBundle":
        """Ensure identifiers line up across nested models."""

        if self.candidate.id != self.application.candidate_id:
            raise ValueError("candidate.id must match application.candidate_id")
        if self.job.id != self.application.job_id:
            raise ValueError("job.id must match application.job_id")
        if self.resume and self.resume.candidate_id != self.candidate.id:
            raise ValueError("resume.candidate_id must match candidate.id")
        return self


class OpenCATSCandidate(BaseModel):
    """Normalized OpenCATS candidate payload."""

    candidate_id: str
    first_name: str
    last_name: str
    email1: EmailStr
    phone1: str | None = None
    city: str | None = None
    country: str | None = None
    summary: str | None = None
    key_skills: str | None = None
    desired_pay_min: float | None = None
    desired_pay_max: float | None = None
    work_type: str | None = None
    availability: str | None = None
    updated_at: datetime


class OpenCATSAttachment(BaseModel):
    """Resume payload to be stored as an OpenCATS attachment."""

    attachment_id: str
    candidate_id: str
    file_name: str
    content_type: str
    content_base64: str
    created_at: datetime


class OpenCATSJobOrder(BaseModel):
    """Job order representation for OpenCATS."""

    job_id: str
    employer_id: str
    title: str
    description: str
    city: str | None = None
    country: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    work_type: str | None = None
    external_id: str | None = None
    updated_at: datetime


class OpenCATSCandidateJobOrder(BaseModel):
    """Join table mapping candidates to job orders with pipeline status."""

    application_id: str
    candidate_id: str
    job_id: str
    status: str
    source: str | None = None
    resume_attachment_id: str | None = None
    submitted_at: datetime
    updated_at: datetime

