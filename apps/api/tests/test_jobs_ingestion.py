from __future__ import annotations

from datetime import datetime, timezone
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.api.app.main import app
from apps.api.app.models import get_job_store, get_schedule_store


client = TestClient(app)


def setup_function() -> None:
    get_job_store().clear()
    get_schedule_store().clear()


def _sample_job_payload(external_id: str, title: str) -> dict[str, object]:
    return {
        "external_id": external_id,
        "title": title,
        "company": "Example Corp",
        "description": "Role description",
        "source_url": "https://jobs.example/demo",
        "location": "Remote",
        "remote": True,
        "employment_type": "full_time",
        "salary_min": 10000000,
        "salary_max": 15000000,
        "currency": "USD",
        "posted_at": datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat(),
        "metadata": {"test": True},
    }


def test_ingest_list_and_schedule_flow() -> None:
    run_id = "run-1"
    payload = {
        "adapter": "demo-board",
        "run_id": run_id,
        "jobs": [_sample_job_payload("job-123", "Senior Platform Engineer")],
    }
    response = client.post("/api/jobs/ingest", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body["run"]["id"] == run_id
    assert body["run"]["created"] == 1
    assert body["run"]["updated"] == 0

    list_response = client.get("/api/jobs")
    assert list_response.status_code == 200
    jobs = list_response.json()["jobs"]
    assert len(jobs) == 1
    job_id = jobs[0]["id"]

    detail_response = client.get(f"/api/jobs/{job_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["external_id"] == "job-123"

    runs_response = client.get("/api/jobs/runs")
    assert runs_response.status_code == 200
    runs = runs_response.json()["runs"]
    assert len(runs) == 1

    schedule_response = client.get("/api/jobs/schedule")
    assert schedule_response.status_code == 200
    schedules = schedule_response.json()["schedules"]
    assert len(schedules) == 1
    assert schedules[0]["last_run_id"] == run_id

    update_payload = {
        "schedules": [
            {"adapter": "demo-board", "interval_minutes": 15, "enabled": True, "metadata": {"priority": "high"}}
        ]
    }
    put_response = client.put("/api/jobs/schedule", json=update_payload)
    assert put_response.status_code == 200
    updated_schedule = put_response.json()["schedules"][0]
    assert updated_schedule["interval_minutes"] == 15
    assert updated_schedule["metadata"]["priority"] == "high"
    assert updated_schedule["last_run_id"] == run_id

    second_run_id = "run-2"
    second_payload = {
        "adapter": "demo-board",
        "run_id": second_run_id,
        "jobs": [_sample_job_payload("job-123", "Principal Platform Engineer")],
    }
    second_response = client.post("/api/jobs/ingest", json=second_payload)
    assert second_response.status_code == 202
    second_body = second_response.json()
    assert second_body["run"]["created"] == 0
    assert second_body["run"]["updated"] == 1

    detail_after_second = client.get(f"/api/jobs/{job_id}")
    assert detail_after_second.status_code == 200
    assert detail_after_second.json()["title"] == "Principal Platform Engineer"

    schedule_after_second = client.get("/api/jobs/schedule")
    assert schedule_after_second.status_code == 200
    assert schedule_after_second.json()["schedules"][0]["last_run_id"] == second_run_id
