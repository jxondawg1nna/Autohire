"""Conversion utilities between AutoHire and OpenCATS models."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .models import (
    ApplicationStatus,
    LocalApplication,
    LocalApplicationBundle,
    LocalCandidate,
    LocalJob,
    LocalResume,
    OpenCATSAttachment,
    OpenCATSCandidate,
    OpenCATSCandidateJobOrder,
    OpenCATSJobOrder,
    WorkType,
)


APPLICATION_STATUS_MAPPING: dict[ApplicationStatus, str] = {
    ApplicationStatus.NEW: "New Lead",
    ApplicationStatus.SCREEN: "Screen",
    ApplicationStatus.INTERVIEW: "Interview",
    ApplicationStatus.OFFER: "Offer",
    ApplicationStatus.HIRED: "Hired",
    ApplicationStatus.REJECTED: "Rejected",
}


def _currency_from_cents(value: int | None) -> float | None:
    if value is None:
        return None
    return round(value / 100, 2)


def _normalize_skills(skills: Iterable[str]) -> str | None:
    unique = sorted({skill.strip().title() for skill in skills if skill.strip()})
    if not unique:
        return None
    return ", ".join(unique)


def _format_work_type(work_type: WorkType | None) -> str | None:
    if work_type is None:
        return None
    return work_type.value.replace("_", " ").title()


def map_candidate_to_opencats(candidate: LocalCandidate) -> OpenCATSCandidate:
    """Convert an AutoHire candidate to an OpenCATS candidate payload."""

    return OpenCATSCandidate(
        candidate_id=candidate.id,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        email1=candidate.email,
        phone1=candidate.phone,
        city=candidate.city,
        country=candidate.country,
        summary=candidate.summary,
        key_skills=_normalize_skills(candidate.skills),
        desired_pay_min=_currency_from_cents(candidate.desired_pay_min),
        desired_pay_max=_currency_from_cents(candidate.desired_pay_max),
        work_type=_format_work_type(candidate.work_type),
        availability=candidate.availability,
        updated_at=candidate.updated_at,
    )


def map_resume_to_opencats(resume: LocalResume, created_at: datetime | None = None) -> OpenCATSAttachment:
    """Convert a stored resume to the OpenCATS attachment structure."""

    return OpenCATSAttachment(
        attachment_id=resume.id,
        candidate_id=resume.candidate_id,
        file_name=resume.file_name,
        content_type=resume.content_type,
        content_base64=resume.as_base64(),
        created_at=created_at or datetime.utcnow(),
    )


def map_job_to_opencats(job: LocalJob) -> OpenCATSJobOrder:
    """Convert an AutoHire job into the OpenCATS job order representation."""

    return OpenCATSJobOrder(
        job_id=job.id,
        employer_id=job.employer_id,
        title=job.title,
        description=job.description,
        city=job.city,
        country=job.country,
        salary_min=_currency_from_cents(job.salary_min),
        salary_max=_currency_from_cents(job.salary_max),
        work_type=_format_work_type(job.work_type),
        external_id=job.external_id,
        updated_at=job.updated_at,
    )


def map_application_to_opencats(bundle: LocalApplicationBundle) -> OpenCATSCandidateJobOrder:
    """Create the OpenCATS join table payload for an application."""

    application: LocalApplication = bundle.application
    status = APPLICATION_STATUS_MAPPING.get(application.status, "Review")

    resume_attachment_id: str | None = None
    if bundle.resume is not None:
        resume_attachment_id = bundle.resume.id

    return OpenCATSCandidateJobOrder(
        application_id=application.id,
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        status=status,
        source=application.source,
        resume_attachment_id=resume_attachment_id,
        submitted_at=application.submitted_at,
        updated_at=application.updated_at,
    )

