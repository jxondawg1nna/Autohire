from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..models import (
    JobRecord,
    ScrapeRun,
    ScrapeSchedule,
    get_job_store,
    get_schedule_store,
)

router = APIRouter()


class JobProvenanceResponse(BaseModel):
    run_id: str
    adapter: str
    scraped_at: datetime
    ingested_at: datetime
    raw_url: str | None = None


class JobResponse(BaseModel):
    id: str
    external_id: str
    title: str
    company: str
    description: str
    source_url: str
    location: str | None = None
    remote: bool | None = None
    employment_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str | None = None
    posted_at: datetime | None = None
    scraped_at: datetime
    source: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    provenance: list[JobProvenanceResponse] = Field(default_factory=list)


class JobListResponse(BaseModel):
    jobs: list[JobResponse]


class JobIngestJob(BaseModel):
    external_id: str
    title: str
    company: str
    description: str
    source_url: str
    location: str | None = None
    remote: bool | None = None
    employment_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str | None = None
    posted_at: datetime | None = None
    scraped_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None


class JobIngestRequest(BaseModel):
    adapter: str
    run_id: str
    jobs: list[JobIngestJob]


class ScrapeRunResponse(BaseModel):
    id: str
    adapter: str
    received: int
    created: int
    updated: int
    ignored: int
    started_at: datetime
    completed_at: datetime


class JobIngestResponse(BaseModel):
    run: ScrapeRunResponse


class ScrapeScheduleEntryPayload(BaseModel):
    adapter: str
    interval_minutes: int = Field(gt=0)
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScrapeScheduleCollectionPayload(BaseModel):
    schedules: list[ScrapeScheduleEntryPayload]


class ScrapeScheduleEntryResponse(BaseModel):
    adapter: str
    interval_minutes: int
    enabled: bool
    last_run_at: datetime | None = None
    last_run_id: str | None = None
    last_result: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScrapeScheduleCollectionResponse(BaseModel):
    schedules: list[ScrapeScheduleEntryResponse]


class ScrapeRunListResponse(BaseModel):
    runs: list[ScrapeRunResponse]


def _job_to_response(record: JobRecord) -> JobResponse:
    return JobResponse.model_validate(record.to_dict())


def _run_to_response(run: ScrapeRun) -> ScrapeRunResponse:
    return ScrapeRunResponse.model_validate(run.to_dict())


def _schedule_to_response(schedule: ScrapeSchedule) -> ScrapeScheduleEntryResponse:
    return ScrapeScheduleEntryResponse.model_validate(schedule.to_dict())


@router.get("", response_model=JobListResponse)
async def list_jobs() -> JobListResponse:
    store = get_job_store()
    jobs = [_job_to_response(job) for job in store.list_jobs()]
    return JobListResponse(jobs=jobs)


@router.post("/ingest", response_model=JobIngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_jobs(payload: JobIngestRequest) -> JobIngestResponse:
    store = get_job_store()
    schedule_store = get_schedule_store()
    normalized_jobs: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for job in payload.jobs:
        data = job.model_dump()
        data["scraped_at"] = data.get("scraped_at") or now
        data["source"] = data.get("source") or payload.adapter
        normalized_jobs.append(data)
    run = store.bulk_ingest(payload.adapter, payload.run_id, normalized_jobs)
    schedule_store.mark_run(run)
    return JobIngestResponse(run=_run_to_response(run))


@router.get("/runs", response_model=ScrapeRunListResponse)
async def list_runs() -> ScrapeRunListResponse:
    store = get_job_store()
    runs = [_run_to_response(run) for run in store.list_runs()]
    return ScrapeRunListResponse(runs=runs)


@router.get("/schedule", response_model=ScrapeScheduleCollectionResponse)
async def list_schedule() -> ScrapeScheduleCollectionResponse:
    schedule_store = get_schedule_store()
    schedules = [_schedule_to_response(entry) for entry in schedule_store.list()]
    return ScrapeScheduleCollectionResponse(schedules=schedules)


@router.put("/schedule", response_model=ScrapeScheduleCollectionResponse)
async def update_schedule(payload: ScrapeScheduleCollectionPayload) -> ScrapeScheduleCollectionResponse:
    schedule_store = get_schedule_store()
    entries = [
        ScrapeSchedule(
            adapter=item.adapter,
            interval_minutes=item.interval_minutes,
            enabled=item.enabled,
            metadata=item.metadata,
        )
        for item in payload.schedules
    ]
    updated = schedule_store.upsert_many(entries)
    return ScrapeScheduleCollectionResponse(schedules=[_schedule_to_response(entry) for entry in updated])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    store = get_job_store()
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _job_to_response(job)
