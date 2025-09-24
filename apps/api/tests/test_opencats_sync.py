from __future__ import annotations

import base64
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.opencats_sync import MAX_RETRIES, SyncScope, get_sync_config


client = TestClient(app)


def _timestamp() -> str:
    return datetime(2024, 1, 1, 12, 0, 0).isoformat()


def _resume_payload(candidate_id: str) -> dict[str, str]:
    return {
        "id": "resume-1",
        "candidate_id": candidate_id,
        "file_name": "resume.pdf",
        "content_type": "application/pdf",
        "data": base64.b64encode(b"resume-bytes").decode("ascii"),
    }


def _candidate_payload(candidate_id: str, employer_id: str) -> dict[str, object]:
    return {
        "id": candidate_id,
        "employer_id": employer_id,
        "email": "candidate@example.com",
        "first_name": "Ava",
        "last_name": "Smith",
        "phone": "+15551230000",
        "city": "Berlin",
        "country": "DE",
        "summary": "Platform engineer",
        "desired_pay_min": 7200000,
        "desired_pay_max": 8600000,
        "work_type": "full_time",
        "availability": "2 weeks",
        "skills": ["python", "fastapi"],
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
    }


def test_sync_candidate_success_and_log_entries() -> None:
    scope = SyncScope.ORGANIZATION.value
    target_id = "org-sync"

    response = client.put(f"/api/opencats/configs/{scope}/{target_id}", json={"enabled": True})
    assert response.status_code == 200

    payload = {
        "scope": scope,
        "target_id": target_id,
        "candidate": _candidate_payload("cand-100", target_id),
        "resume": _resume_payload("cand-100"),
    }

    result = client.post("/api/opencats/sync/candidate", json=payload)
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "success"
    assert data["payload"]["candidate"]["candidate_id"] == "cand-100"

    logs = client.get(
        "/api/opencats/logs",
        params={"scope": scope, "target_id": target_id, "limit": 5},
    ).json()
    assert len(logs["items"]) >= 2
    assert logs["items"][0]["status"] in {"success", "pending"}

    reconcile = client.post("/api/opencats/reconcile", json={"scope": scope, "target_id": target_id})
    assert reconcile.status_code == 200
    reconcile_payload = reconcile.json()
    assert reconcile_payload["status"] == "success"
    assert reconcile_payload["payload"]["scope"] == scope


def test_sync_candidate_failure_uses_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    scope = SyncScope.ORGANIZATION.value
    target_id = "org-error"

    client.put(f"/api/opencats/configs/{scope}/{target_id}", json={"enabled": True})

    def _raise_error(*args, **kwargs):  # pragma: no cover - invoked via monkeypatch
        raise ValueError("boom")

    monkeypatch.setattr("app.tasks.opencats.OpenCATSClient.build_candidate_payload", _raise_error)

    payload = {
        "scope": scope,
        "target_id": target_id,
        "candidate": _candidate_payload("cand-200", target_id),
        "resume": _resume_payload("cand-200"),
    }

    response = client.post("/api/opencats/sync/candidate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["retry"] is False

    config = get_sync_config(SyncScope.ORGANIZATION, target_id)
    assert config is not None
    assert config.retries == MAX_RETRIES
    assert config.last_status.value == "failed"

