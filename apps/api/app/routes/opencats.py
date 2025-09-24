"""API routes for OpenCATS synchronization."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas.opencats import (
    ApplicationSyncRequest,
    CandidateSyncRequest,
    ConfigListResponse,
    JobSyncRequest,
    LogListResponse,
    ReconcileRequest,
    SyncConfigResponse,
    SyncConfigUpdate,
    SyncLogResponse,
    SyncResult,
)
from app.services.opencats_sync import (
    SyncScope,
    enqueue_sync_application,
    enqueue_sync_candidate,
    enqueue_sync_job,
    get_recent_logs,
    get_sync_config,
    list_sync_configs,
    set_sync_enabled,
    trigger_reconcile,
)


router = APIRouter()


@router.get("/configs", response_model=ConfigListResponse)
def list_configs(scope: SyncScope | None = Query(default=None)) -> ConfigListResponse:
    configs = list_sync_configs(scope=scope)
    return ConfigListResponse(items=[SyncConfigResponse.from_config(cfg) for cfg in configs])


@router.get("/configs/{scope}/{target_id}", response_model=SyncConfigResponse)
def get_config(scope: SyncScope, target_id: str) -> SyncConfigResponse:
    config = get_sync_config(scope, target_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Sync configuration not found")
    return SyncConfigResponse.from_config(config)


@router.put("/configs/{scope}/{target_id}", response_model=SyncConfigResponse)
def update_config(scope: SyncScope, target_id: str, payload: SyncConfigUpdate) -> SyncConfigResponse:
    config = set_sync_enabled(scope, target_id, payload.enabled)
    return SyncConfigResponse.from_config(config)


@router.post("/sync/candidate", response_model=SyncResult)
def sync_candidate(request: CandidateSyncRequest) -> SyncResult:
    result = enqueue_sync_candidate(request.scope, request.target_id, request.candidate, request.resume)
    return SyncResult(**result)


@router.post("/sync/job", response_model=SyncResult)
def sync_job(request: JobSyncRequest) -> SyncResult:
    result = enqueue_sync_job(request.scope, request.target_id, request.job)
    return SyncResult(**result)


@router.post("/sync/application", response_model=SyncResult)
def sync_application(request: ApplicationSyncRequest) -> SyncResult:
    result = enqueue_sync_application(request.scope, request.target_id, request.bundle)
    return SyncResult(**result)


@router.post("/reconcile", response_model=SyncResult)
def reconcile(request: ReconcileRequest) -> SyncResult:
    result = trigger_reconcile(request.scope, request.target_id)
    return SyncResult(**result)


@router.get("/logs", response_model=LogListResponse)
def list_logs(
    scope: SyncScope | None = Query(default=None),
    target_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> LogListResponse:
    logs = get_recent_logs(scope=scope, target_id=target_id, limit=limit)
    return LogListResponse(items=[SyncLogResponse.from_log(entry) for entry in logs])

