from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Response, status

from ..models.automation import ApplicationLogCreate, ApplicationLogEntry, AutomationStep

router = APIRouter()


def _seed_logs() -> list[ApplicationLogEntry]:
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(hours=6)
    return [
        ApplicationLogEntry(
            id="log-native-success",
            rule_id="design-remote",
            job_id="job-4231",
            job_title="Senior Product Designer",
            company="Canvas Labs",
            channel="native",
            status="submitted",
            submitted_at=earlier,
            audit_trail=[
                AutomationStep(
                    name="render_resume",
                    status="completed",
                    timestamp=earlier - timedelta(minutes=3),
                    detail="Rendered product-story template",
                ),
                AutomationStep(
                    name="render_cover_letter",
                    status="completed",
                    timestamp=earlier - timedelta(minutes=2),
                    detail="Generated cover letter with personalization",
                ),
                AutomationStep(
                    name="submit_native_application",
                    status="completed",
                    timestamp=earlier,
                    detail="Submitted via ATS API",
                ),
            ],
            notes="Resume and cover letter uploaded. Awaiting recruiter review.",
        ),
        ApplicationLogEntry(
            id="log-playwright-failure",
            rule_id="growth-marketing",
            job_id="job-9654",
            job_title="Lifecycle Marketing Manager",
            company="Velocity Labs",
            channel="playwright",
            status="failed",
            submitted_at=now - timedelta(hours=2),
            audit_trail=[
                AutomationStep(
                    name="launch_browser",
                    status="completed",
                    timestamp=now - timedelta(hours=2, minutes=5),
                    detail="Started Chromium via Playwright",
                ),
                AutomationStep(
                    name="fill_application_form",
                    status="failed",
                    timestamp=now - timedelta(hours=2),
                    detail="Captcha challenge blocked automation",
                ),
            ],
            notes="Manual follow-up recommended due to captcha interruption.",
        ),
    ]


_logs_store: dict[str, ApplicationLogEntry] = {log.id: log for log in _seed_logs()}


@router.get("", response_model=list[ApplicationLogEntry])
async def list_application_logs(rule_id: str | None = None) -> list[ApplicationLogEntry]:
    """Return application runs, optionally scoped to a rule."""

    if not rule_id:
        return sorted(_logs_store.values(), key=lambda entry: entry.submitted_at, reverse=True)

    filtered = [log for log in _logs_store.values() if log.rule_id == rule_id]
    return sorted(filtered, key=lambda entry: entry.submitted_at, reverse=True)


@router.get("/{log_id}", response_model=ApplicationLogEntry)
async def get_application_log(log_id: str) -> ApplicationLogEntry:
    log = _logs_store.get(log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found")
    return log


@router.post("", response_model=ApplicationLogEntry, status_code=status.HTTP_201_CREATED)
async def create_application_log(payload: ApplicationLogCreate) -> ApplicationLogEntry:
    log_id = str(uuid4())
    submitted_at = payload.submitted_at or datetime.now(timezone.utc)
    log = ApplicationLogEntry(id=log_id, submitted_at=submitted_at, **payload.model_dump(exclude={"submitted_at"}))
    _logs_store[log_id] = log
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application_log(log_id: str) -> Response:
    if log_id not in _logs_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found")

    del _logs_store[log_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
