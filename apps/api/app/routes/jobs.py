"""Job and pipeline endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..models import (
    Application,
    EmployerRole,
    Job,
    JobCreateRequest,
    JobPipeline,
    create_job,
    get_job_for_employer,
    get_job_pipeline,
    list_job_applications,
    list_jobs_for_employer,
)
from .dependencies import EmployerContext, require_roles

router = APIRouter()


@router.get("", response_model=list[Job])
async def list_jobs(
    employer_id: str,
    _context: EmployerContext = Depends(
        require_roles(EmployerRole.OWNER, EmployerRole.RECRUITER, EmployerRole.HIRING_MANAGER)
    ),
) -> list[Job]:
    """List jobs owned by the employer."""

    return list_jobs_for_employer(employer_id)


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(
    employer_id: str,
    payload: JobCreateRequest,
    _context: EmployerContext = Depends(require_roles(EmployerRole.OWNER, EmployerRole.RECRUITER)),
) -> Job:
    """Create a new job within the employer scope."""

    try:
        return create_job(employer_id, payload)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{job_id}", response_model=Job)
async def get_job_detail(
    employer_id: str,
    job_id: str,
    _context: EmployerContext = Depends(
        require_roles(
            EmployerRole.OWNER,
            EmployerRole.RECRUITER,
            EmployerRole.HIRING_MANAGER,
            EmployerRole.CONTRIBUTOR,
        )
    ),
) -> Job:
    """Return details for a job."""

    job = get_job_for_employer(employer_id, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job


@router.get("/{job_id}/pipeline", response_model=JobPipeline)
async def get_job_pipeline_detail(
    employer_id: str,
    job_id: str,
    _context: EmployerContext = Depends(
        require_roles(
            EmployerRole.OWNER,
            EmployerRole.RECRUITER,
            EmployerRole.HIRING_MANAGER,
            EmployerRole.CONTRIBUTOR,
        )
    ),
) -> JobPipeline:
    """Return the pipeline configuration for the job."""

    pipeline = get_job_pipeline(employer_id, job_id)
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found.")
    return pipeline


@router.get("/{job_id}/applications", response_model=list[Application])
async def list_job_application_detail(
    employer_id: str,
    job_id: str,
    _context: EmployerContext = Depends(
        require_roles(EmployerRole.OWNER, EmployerRole.RECRUITER, EmployerRole.HIRING_MANAGER)
    ),
) -> list[Application]:
    """Return applications submitted to the job."""

    # ensure the job exists before returning applications
    job = get_job_for_employer(employer_id, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return list_job_applications(employer_id, job_id)
