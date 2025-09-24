"""FastAPI application for Autohire."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI

from . import models, repository
from .database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Autohire API", version="1.0.0", lifespan=lifespan)


@app.post("/jobs", response_model=models.Job, status_code=201)
def create_job(job: models.JobCreate) -> models.Job:
    return repository.create_job(job)


@app.get("/jobs", response_model=list[models.Job])
def get_jobs() -> list[models.Job]:
    return repository.list_jobs()


@app.get("/jobs/{job_id}", response_model=models.Job)
def get_job(job_id: int) -> models.Job:
    return repository.get_job(job_id)


@app.post("/candidates", response_model=models.Candidate, status_code=201)
def create_candidate(candidate: models.CandidateCreate) -> models.Candidate:
    return repository.create_candidate(candidate)


@app.get("/candidates", response_model=list[models.Candidate])
def get_candidates() -> list[models.Candidate]:
    return repository.list_candidates()


@app.get("/candidates/{candidate_id}", response_model=models.Candidate)
def get_candidate(candidate_id: int) -> models.Candidate:
    return repository.get_candidate(candidate_id)


@app.post("/applications", response_model=models.Application, status_code=201)
def create_application(application: models.ApplicationCreate) -> models.Application:
    return repository.create_application(application)


@app.get("/applications", response_model=list[models.Application])
def get_applications(status: Optional[str] = None) -> list[models.Application]:
    return repository.list_applications(status)


@app.get("/applications/{application_id}", response_model=models.Application)
def get_application(application_id: int) -> models.Application:
    return repository.get_application(application_id)


@app.patch("/applications/{application_id}", response_model=models.Application)
def update_application_status(application_id: int, payload: models.ApplicationStatusUpdate) -> models.Application:
    return repository.update_application_status(application_id, payload)


@app.post("/applications/{application_id}/interviews", response_model=models.Interview, status_code=201)
def create_interview(application_id: int, interview: models.InterviewCreate) -> models.Interview:
    return repository.create_interview(application_id, interview)


@app.get("/applications/{application_id}/interviews", response_model=list[models.Interview])
def list_interviews(application_id: int) -> list[models.Interview]:
    return repository.list_interviews(application_id)


@app.get("/pipeline/summary")
def pipeline_summary() -> dict:
    return repository.get_pipeline_summary()
