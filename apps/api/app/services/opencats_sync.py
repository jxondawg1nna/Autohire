"""State management for OpenCATS synchronization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Iterable, List, Tuple

from app.opencats.models import LocalApplicationBundle, LocalCandidate, LocalJob, LocalResume


class SyncScope(str, Enum):
    ORGANIZATION = "organization"
    JOB = "job"


class SyncEntityType(str, Enum):
    CANDIDATE = "candidate"
    JOB = "job"
    APPLICATION = "application"
    RECONCILIATION = "reconciliation"


class SyncStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    DISABLED = "disabled"


@dataclass
class SyncConfig:
    scope: SyncScope
    target_id: str
    enabled: bool = False
    last_synced_at: datetime | None = None
    last_attempted_at: datetime | None = None
    last_status: SyncStatus = SyncStatus.DISABLED
    retries: int = 0
    error: str | None = None


@dataclass
class SyncLogEntry:
    timestamp: datetime
    scope: SyncScope
    target_id: str
    entity_type: SyncEntityType
    status: SyncStatus
    message: str
    retry_count: int = 0


MAX_RETRIES = 3

_SYNC_CONFIGS: Dict[Tuple[SyncScope, str], SyncConfig] = {}
_SYNC_LOGS: List[SyncLogEntry] = []


def _make_key(scope: SyncScope, target_id: str) -> Tuple[SyncScope, str]:
    return scope, target_id


def _log_entry(entry: SyncLogEntry) -> SyncLogEntry:
    _SYNC_LOGS.append(entry)
    return entry


def ensure_sync_config(scope: SyncScope, target_id: str) -> SyncConfig:
    key = _make_key(scope, target_id)
    if key not in _SYNC_CONFIGS:
        _SYNC_CONFIGS[key] = SyncConfig(scope=scope, target_id=target_id)
    return _SYNC_CONFIGS[key]


def set_sync_enabled(scope: SyncScope, target_id: str, enabled: bool) -> SyncConfig:
    config = ensure_sync_config(scope, target_id)
    config.enabled = enabled
    config.last_status = SyncStatus.DISABLED if not enabled else config.last_status
    if not enabled:
        config.error = None
        config.retries = 0
    return config


def get_sync_config(scope: SyncScope, target_id: str) -> SyncConfig | None:
    return _SYNC_CONFIGS.get(_make_key(scope, target_id))


def list_sync_configs(scope: SyncScope | None = None) -> List[SyncConfig]:
    configs: Iterable[SyncConfig]
    if scope is None:
        configs = _SYNC_CONFIGS.values()
    else:
        configs = [cfg for cfg in _SYNC_CONFIGS.values() if cfg.scope == scope]
    return sorted(configs, key=lambda cfg: (cfg.scope.value, cfg.target_id))


def record_sync_attempt(scope: SyncScope, target_id: str, entity_type: SyncEntityType) -> SyncLogEntry:
    config = ensure_sync_config(scope, target_id)
    config.last_attempted_at = datetime.utcnow()
    config.last_status = SyncStatus.PENDING
    return _log_entry(
        SyncLogEntry(
            timestamp=config.last_attempted_at,
            scope=scope,
            target_id=target_id,
            entity_type=entity_type,
            status=SyncStatus.PENDING,
            message="Synchronization started",
            retry_count=config.retries,
        )
    )


def record_sync_success(scope: SyncScope, target_id: str, entity_type: SyncEntityType, message: str) -> SyncLogEntry:
    config = ensure_sync_config(scope, target_id)
    config.last_synced_at = datetime.utcnow()
    config.last_status = SyncStatus.SUCCESS
    config.error = None
    config.retries = 0
    return _log_entry(
        SyncLogEntry(
            timestamp=config.last_synced_at,
            scope=scope,
            target_id=target_id,
            entity_type=entity_type,
            status=SyncStatus.SUCCESS,
            message=message,
            retry_count=config.retries,
        )
    )


def record_sync_failure(scope: SyncScope, target_id: str, entity_type: SyncEntityType, message: str) -> tuple[SyncLogEntry, bool]:
    config = ensure_sync_config(scope, target_id)
    config.retries += 1
    config.last_status = SyncStatus.FAILED
    config.error = message
    timestamp = datetime.utcnow()
    entry = _log_entry(
        SyncLogEntry(
            timestamp=timestamp,
            scope=scope,
            target_id=target_id,
            entity_type=entity_type,
            status=SyncStatus.FAILED,
            message=message,
            retry_count=config.retries,
        )
    )
    should_retry = config.retries < MAX_RETRIES
    return entry, should_retry


def record_sync_skip(scope: SyncScope, target_id: str, entity_type: SyncEntityType, reason: str) -> SyncLogEntry:
    config = ensure_sync_config(scope, target_id)
    config.last_status = SyncStatus.SKIPPED
    config.error = None
    return _log_entry(
        SyncLogEntry(
            timestamp=datetime.utcnow(),
            scope=scope,
            target_id=target_id,
            entity_type=entity_type,
            status=SyncStatus.SKIPPED,
            message=reason,
            retry_count=config.retries,
        )
    )


def get_recent_logs(scope: SyncScope | None = None, target_id: str | None = None, limit: int = 20) -> List[SyncLogEntry]:
    filtered = [
        entry
        for entry in _SYNC_LOGS
        if (scope is None or entry.scope == scope) and (target_id is None or entry.target_id == target_id)
    ]
    filtered.sort(key=lambda entry: entry.timestamp, reverse=True)
    return filtered[:limit]


def reset_sync_state() -> None:
    _SYNC_CONFIGS.clear()
    _SYNC_LOGS.clear()


def serialize_sync_config(config: SyncConfig) -> dict[str, object]:
    return {
        "scope": config.scope.value,
        "target_id": config.target_id,
        "enabled": config.enabled,
        "last_synced_at": config.last_synced_at.isoformat() if config.last_synced_at else None,
        "last_attempted_at": config.last_attempted_at.isoformat() if config.last_attempted_at else None,
        "last_status": config.last_status.value,
        "retries": config.retries,
        "error": config.error,
    }


def serialize_log_entry(entry: SyncLogEntry) -> dict[str, object]:
    return {
        "timestamp": entry.timestamp.isoformat(),
        "scope": entry.scope.value,
        "target_id": entry.target_id,
        "entity_type": entry.entity_type.value,
        "status": entry.status.value,
        "message": entry.message,
        "retry_count": entry.retry_count,
    }


def enqueue_sync_candidate(scope: SyncScope, target_id: str, candidate: LocalCandidate, resume: LocalResume | None = None) -> dict[str, object]:
    from app.tasks.opencats import sync_entity_task

    if not ensure_sync_config(scope, target_id).enabled:
        entry = record_sync_skip(scope, target_id, SyncEntityType.CANDIDATE, "Sync disabled for scope")
        return {"status": entry.status.value, "message": entry.message}

    payload = {
        "entity": candidate.model_dump(mode="json"),
        "resume": _serialize_resume(resume),
    }
    return _execute_with_retries(
        sync_entity_task,
        scope,
        target_id,
        SyncEntityType.CANDIDATE,
        payload,
    )


def enqueue_sync_job(scope: SyncScope, target_id: str, job: LocalJob) -> dict[str, object]:
    from app.tasks.opencats import sync_entity_task

    if not ensure_sync_config(scope, target_id).enabled:
        entry = record_sync_skip(scope, target_id, SyncEntityType.JOB, "Sync disabled for scope")
        return {"status": entry.status.value, "message": entry.message}

    payload = {"entity": job.model_dump(mode="json")}
    return _execute_with_retries(
        sync_entity_task,
        scope,
        target_id,
        SyncEntityType.JOB,
        payload,
    )


def enqueue_sync_application(scope: SyncScope, target_id: str, bundle: LocalApplicationBundle) -> dict[str, object]:
    from app.tasks.opencats import sync_entity_task

    if not ensure_sync_config(scope, target_id).enabled:
        entry = record_sync_skip(scope, target_id, SyncEntityType.APPLICATION, "Sync disabled for scope")
        return {"status": entry.status.value, "message": entry.message}

    bundle_payload = bundle.model_dump(mode="json")
    if bundle.resume is not None and bundle_payload.get("resume") is not None:
        bundle_payload["resume"]["data"] = bundle.resume.as_base64()
    payload = {"entity": bundle_payload}
    return _execute_with_retries(
        sync_entity_task,
        scope,
        target_id,
        SyncEntityType.APPLICATION,
        payload,
    )


def trigger_reconcile(scope: SyncScope, target_id: str) -> dict[str, object]:
    from app.tasks.opencats import reconcile_task

    payload = {"scope": scope.value, "target_id": target_id}
    result = reconcile_task.apply_async(args=[scope.value, target_id]).get()
    return result | {"payload": payload}


def _execute_with_retries(task, scope: SyncScope, target_id: str, entity_type: SyncEntityType, payload: dict[str, object]) -> dict[str, object]:
    attempt = 0
    result: dict[str, object] | None = None
    while attempt <= MAX_RETRIES:
        async_result = task.apply_async(args=[scope.value, target_id, entity_type.value, payload])
        result = async_result.get()
        if result.get("status") != SyncStatus.FAILED.value or not result.get("retry"):
            break
        attempt += 1
    return result or {"status": SyncStatus.FAILED.value, "message": "Task execution failed"}


def _serialize_resume(resume: LocalResume | None) -> dict[str, object] | None:
    if resume is None:
        return None
    payload = resume.model_dump(mode="json")
    payload["data"] = resume.as_base64()
    return payload

