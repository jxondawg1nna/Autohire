from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from autohire.api import app
from autohire.database import init_db, set_db_path


@pytest.fixture(autouse=True)
def temp_database(tmp_path: Path) -> Iterator[None]:
    db_path = tmp_path / "autohire_test.db"
    set_db_path(db_path)
    init_db()
    yield


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_create_job_candidate_application_flow(client: TestClient) -> None:
    job_payload = {"title": "Backend Engineer", "description": "Build APIs", "department": "Engineering"}
    job = client.post("/jobs", json=job_payload)
    assert job.status_code == 201
    job_id = job.json()["id"]

    candidate_payload = {
        "name": "Alex Johnson",
        "email": "alex@example.com",
        "resume": "5 years of backend experience.",
    }
    candidate = client.post("/candidates", json=candidate_payload)
    assert candidate.status_code == 201
    candidate_id = candidate.json()["id"]

    application_payload = {"candidate_id": candidate_id, "job_id": job_id}
    application_response = client.post("/applications", json=application_payload)
    assert application_response.status_code == 201
    application = application_response.json()
    assert application["status"] == "applied"

    update_response = client.patch(
        f"/applications/{application['id']}", json={"status": "interview"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "interview"

    summary = client.get("/pipeline/summary")
    assert summary.status_code == 200
    data = summary.json()
    assert data["total_jobs"] == 1
    assert data["total_candidates"] == 1
    assert data["applications_per_status"]["interview"] == 1


def test_duplicate_candidate_email_returns_bad_request(client: TestClient) -> None:
    candidate_payload = {
        "name": "Jordan Lee",
        "email": "jordan@example.com",
        "resume": "Seasoned recruiter.",
    }
    first_response = client.post("/candidates", json=candidate_payload)
    assert first_response.status_code == 201

    second_response = client.post("/candidates", json=candidate_payload)
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Candidate with this email already exists"


def test_interview_scheduling_and_listing(client: TestClient) -> None:
    job_id = client.post(
        "/jobs", json={"title": "Designer", "description": "Design products", "department": "Design"}
    ).json()["id"]
    candidate_id = client.post(
        "/candidates",
        json={"name": "Taylor Smith", "email": "taylor@example.com", "resume": "Design portfolio."},
    ).json()["id"]
    application_id = client.post(
        "/applications", json={"candidate_id": candidate_id, "job_id": job_id}
    ).json()["id"]

    scheduled_at = (datetime.utcnow() + timedelta(days=1)).replace(microsecond=0)
    interview_payload = {
        "scheduled_at": scheduled_at.isoformat(),
        "interviewer": "Morgan",
        "feedback": "Great communication",
        "result": "pending",
    }
    create_response = client.post(
        f"/applications/{application_id}/interviews", json=interview_payload
    )
    assert create_response.status_code == 201

    interviews_response = client.get(f"/applications/{application_id}/interviews")
    assert interviews_response.status_code == 200
    interviews = interviews_response.json()
    assert len(interviews) == 1
    assert interviews[0]["interviewer"] == "Morgan"
    assert interviews[0]["result"] == "pending"


def test_application_status_filtering(client: TestClient) -> None:
    job_id = client.post(
        "/jobs", json={"title": "QA Analyst", "description": "Test software", "department": "QA"}
    ).json()["id"]
    candidate_a = client.post(
        "/candidates",
        json={"name": "Chris A", "email": "chris.a@example.com", "resume": "QA expert."},
    ).json()["id"]
    candidate_b = client.post(
        "/candidates",
        json={"name": "Chris B", "email": "chris.b@example.com", "resume": "QA lead."},
    ).json()["id"]

    application_a = client.post(
        "/applications", json={"candidate_id": candidate_a, "job_id": job_id}
    ).json()
    application_b = client.post(
        "/applications", json={"candidate_id": candidate_b, "job_id": job_id}
    ).json()

    client.patch(f"/applications/{application_a['id']}", json={"status": "offer"})
    client.patch(f"/applications/{application_b['id']}", json={"status": "rejected"})

    offers = client.get("/applications", params={"status": "offer"})
    assert offers.status_code == 200
    assert [app["id"] for app in offers.json()] == [application_a["id"]]

    rejected = client.get("/applications", params={"status": "rejected"})
    assert rejected.status_code == 200
    assert [app["id"] for app in rejected.json()] == [application_b["id"]]

    invalid = client.get("/applications", params={"status": "unknown"})
    assert invalid.status_code == 400
