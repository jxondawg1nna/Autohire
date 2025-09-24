"""Celery tasks orchestrating synchronization with OpenCATS."""

from __future__ import annotations

import base64
from typing import Any, Dict

from pydantic import ValidationError

from app.opencats import OpenCATSClient
from app.opencats.models import LocalApplicationBundle, LocalCandidate, LocalJob, LocalResume
from app.services.opencats_sync import (
    SyncEntityType,
    SyncScope,
    SyncStatus,
    record_sync_attempt,
    record_sync_failure,
    record_sync_success,
)

from .celery_app import celery_app


def _decode_resume_payload(payload: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if payload is None:
        return None
    if "data" in payload and isinstance(payload["data"], str):
        payload = payload.copy()
        payload["data"] = base64.b64decode(payload["data"])
    return payload


@celery_app.task(name="opencats.sync_entity")
def sync_entity_task(scope: str, target_id: str, entity_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    scope_enum = SyncScope(scope)
    entity_enum = SyncEntityType(entity_type)
    record_sync_attempt(scope_enum, target_id, entity_enum)
    client = OpenCATSClient()

    try:
        if entity_enum is SyncEntityType.CANDIDATE:
            candidate = LocalCandidate.model_validate(payload["entity"])
            resume_data = _decode_resume_payload(payload.get("resume"))
            resume = LocalResume.model_validate(resume_data) if resume_data else None
            body = client.build_candidate_payload(candidate, resume)
            record_sync_success(
                scope_enum,
                target_id,
                entity_enum,
                f"Candidate {candidate.id} prepared for sync",
            )
            return {"status": SyncStatus.SUCCESS.value, "payload": body}

        if entity_enum is SyncEntityType.JOB:
            job = LocalJob.model_validate(payload["entity"])
            body = client.build_job_payload(job)
            record_sync_success(
                scope_enum,
                target_id,
                entity_enum,
                f"Job {job.id} prepared for sync",
            )
            return {"status": SyncStatus.SUCCESS.value, "payload": body}

        if entity_enum is SyncEntityType.APPLICATION:
            bundle_payload = payload["entity"].copy()
            resume_payload = _decode_resume_payload(bundle_payload.get("resume"))
            if resume_payload is not None:
                bundle_payload["resume"] = resume_payload
            bundle = LocalApplicationBundle.model_validate(bundle_payload)
            body = client.build_application_payload(bundle)
            record_sync_success(
                scope_enum,
                target_id,
                entity_enum,
                f"Application {bundle.application.id} prepared for sync",
            )
            return {"status": SyncStatus.SUCCESS.value, "payload": body}

        raise ValueError(f"Unsupported entity type '{entity_type}'")

    except (ValidationError, KeyError, ValueError) as exc:
        _, should_retry = record_sync_failure(
            scope_enum,
            target_id,
            entity_enum,
            f"Validation failed: {exc}",
        )
        return {"status": SyncStatus.FAILED.value, "error": str(exc), "retry": should_retry}
    except Exception as exc:  # pragma: no cover - defensive guard
        _, should_retry = record_sync_failure(
            scope_enum,
            target_id,
            entity_enum,
            f"Unexpected error: {exc}",
        )
        return {"status": SyncStatus.FAILED.value, "error": str(exc), "retry": should_retry}


@celery_app.task(name="opencats.reconcile")
def reconcile_task(scope: str, target_id: str) -> Dict[str, Any]:
    scope_enum = SyncScope(scope)
    entity_enum = SyncEntityType.RECONCILIATION
    record_sync_attempt(scope_enum, target_id, entity_enum)
    client = OpenCATSClient()
    payload = client.build_reconcile_payload(scope, target_id)
    record_sync_success(scope_enum, target_id, entity_enum, "Reconciliation request prepared")
    return {"status": SyncStatus.SUCCESS.value, "payload": payload}

