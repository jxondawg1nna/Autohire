"""API schemas for OpenCATS synchronization endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.opencats.models import LocalApplicationBundle, LocalCandidate, LocalJob, LocalResume
from app.services.opencats_sync import (
    SyncConfig,
    SyncEntityType,
    SyncLogEntry,
    SyncScope,
    SyncStatus,
)


class SyncConfigUpdate(BaseModel):
    enabled: bool = Field(default=True, description="Enable or disable synchronization for the scope")


class SyncConfigResponse(BaseModel):
    scope: SyncScope
    target_id: str
    enabled: bool
    last_synced_at: datetime | None = None
    last_attempted_at: datetime | None = None
    last_status: SyncStatus
    retries: int
    error: str | None = None

    @classmethod
    def from_config(cls, config: SyncConfig) -> "SyncConfigResponse":
        return cls(
            scope=config.scope,
            target_id=config.target_id,
            enabled=config.enabled,
            last_synced_at=config.last_synced_at,
            last_attempted_at=config.last_attempted_at,
            last_status=config.last_status,
            retries=config.retries,
            error=config.error,
        )


class SyncLogResponse(BaseModel):
    timestamp: datetime
    scope: SyncScope
    target_id: str
    entity_type: SyncEntityType
    status: SyncStatus
    message: str
    retry_count: int

    @classmethod
    def from_log(cls, log: SyncLogEntry) -> "SyncLogResponse":
        return cls(
            timestamp=log.timestamp,
            scope=log.scope,
            target_id=log.target_id,
            entity_type=log.entity_type,
            status=log.status,
            message=log.message,
            retry_count=log.retry_count,
        )


class CandidateSyncRequest(BaseModel):
    scope: SyncScope
    target_id: str
    candidate: LocalCandidate
    resume: LocalResume | None = None


class JobSyncRequest(BaseModel):
    scope: SyncScope
    target_id: str
    job: LocalJob


class ApplicationSyncRequest(BaseModel):
    scope: SyncScope
    target_id: str
    bundle: LocalApplicationBundle


class ReconcileRequest(BaseModel):
    scope: SyncScope
    target_id: str


class SyncResult(BaseModel):
    status: str
    message: str | None = None
    payload: dict | None = None
    error: str | None = None
    retry: bool | None = None


class ConfigListResponse(BaseModel):
    items: List[SyncConfigResponse]


class LogListResponse(BaseModel):
    items: List[SyncLogResponse]

