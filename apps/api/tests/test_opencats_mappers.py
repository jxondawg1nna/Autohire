from __future__ import annotations

from datetime import datetime
from app.opencats.mappers import (
    map_application_to_opencats,
    map_candidate_to_opencats,
    map_job_to_opencats,
    map_resume_to_opencats,
)
from app.opencats.models import (
    ApplicationStatus,
    LocalApplication,
    LocalApplicationBundle,
    LocalCandidate,
    LocalJob,
    LocalResume,
    WorkType,
)


def _now() -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0)


def test_map_candidate_to_opencats_rounds_currency_and_skills() -> None:
    candidate = LocalCandidate(
        id="cand-1",
        employer_id="org-1",
        email="person@example.com",
        first_name="Jane",
        last_name="Doe",
        phone="+15551234567",
        city="Berlin",
        country="DE",
        summary="Seasoned data engineer",
        desired_pay_min=8800000,
        desired_pay_max=10500000,
        work_type=WorkType.FULL_TIME,
        availability="Immediate",
        skills=["Python", "sql", "Python"],
        created_at=_now(),
        updated_at=_now(),
    )

    result = map_candidate_to_opencats(candidate)

    assert result.desired_pay_min == 88000.0
    assert result.desired_pay_max == 105000.0
    assert result.key_skills == "Python, Sql"
    assert result.work_type == "Full Time"


def test_map_resume_to_opencats_base64_encodes_content() -> None:
    resume = LocalResume(
        id="resume-1",
        candidate_id="cand-1",
        file_name="cv.pdf",
        content_type="application/pdf",
        data=b"pdf-bytes",
    )

    mapped = map_resume_to_opencats(resume, created_at=_now())
    assert mapped.content_base64 == resume.as_base64()
    assert mapped.candidate_id == resume.candidate_id


def test_map_job_to_opencats_preserves_external_identifier() -> None:
    job = LocalJob(
        id="job-1",
        employer_id="org-1",
        title="Senior Engineer",
        description="Design systems",
        city="Munich",
        country="DE",
        salary_min=9000000,
        salary_max=12000000,
        work_type=WorkType.CONTRACT,
        external_id="ATS-123",
        created_at=_now(),
        updated_at=_now(),
    )

    mapped = map_job_to_opencats(job)
    assert mapped.external_id == "ATS-123"
    assert mapped.salary_min == 90000.0
    assert mapped.work_type == "Contract"


def test_map_application_to_opencats_sets_status_and_resume_link() -> None:
    candidate = LocalCandidate(
        id="cand-1",
        employer_id="org-1",
        email="person@example.com",
        first_name="Jane",
        last_name="Doe",
        phone=None,
        city="Berlin",
        country="DE",
        summary=None,
        desired_pay_min=None,
        desired_pay_max=None,
        work_type=None,
        availability=None,
        skills=[],
        created_at=_now(),
        updated_at=_now(),
    )
    job = LocalJob(
        id="job-1",
        employer_id="org-1",
        title="Engineer",
        description="Build things",
        city="Berlin",
        country="DE",
        salary_min=None,
        salary_max=None,
        work_type=None,
        external_id=None,
        created_at=_now(),
        updated_at=_now(),
    )
    application = LocalApplication(
        id="app-1",
        employer_id="org-1",
        candidate_id=candidate.id,
        job_id=job.id,
        status=ApplicationStatus.INTERVIEW,
        source="Referral",
        resume_id="resume-1",
        submitted_at=_now(),
        updated_at=_now(),
    )
    resume = LocalResume(
        id="resume-1",
        candidate_id=candidate.id,
        file_name="cv.pdf",
        content_type="application/pdf",
        data=b"binary",
    )

    bundle = LocalApplicationBundle(application=application, candidate=candidate, job=job, resume=resume)

    mapped = map_application_to_opencats(bundle)
    assert mapped.status == "Interview"
    assert mapped.resume_attachment_id == "resume-1"
    assert mapped.application_id == application.id

