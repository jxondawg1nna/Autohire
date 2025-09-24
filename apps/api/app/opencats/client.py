"""OpenCATS client helpers used by synchronization tasks."""

from __future__ import annotations

from typing import Any, Dict

from app.core.config import get_settings

from . import mappers
from .models import LocalApplicationBundle, LocalCandidate, LocalJob, LocalResume


class OpenCATSClient:
    """Lightweight helper producing OpenCATS payloads."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.opencats_base_url
        self.api_key = api_key or settings.opencats_api_key

    # ------------------------------------------------------------------
    # Payload builders
    # ------------------------------------------------------------------
    def build_candidate_payload(
        self, candidate: LocalCandidate, resume: LocalResume | None = None
    ) -> Dict[str, Any]:
        candidate_payload = mappers.map_candidate_to_opencats(candidate).model_dump(by_alias=True)
        attachments: list[dict[str, Any]] = []
        if resume is not None:
            attachments.append(mappers.map_resume_to_opencats(resume).model_dump(by_alias=True))

        return {
            "candidate": candidate_payload,
            "attachments": attachments,
            "endpoint": f"{self.base_url}/candidate",
        }

    def build_job_payload(self, job: LocalJob) -> Dict[str, Any]:
        job_payload = mappers.map_job_to_opencats(job).model_dump(by_alias=True)
        return {
            "joborder": job_payload,
            "endpoint": f"{self.base_url}/joborder",
        }

    def build_application_payload(self, bundle: LocalApplicationBundle) -> Dict[str, Any]:
        candidate = mappers.map_candidate_to_opencats(bundle.candidate).model_dump(by_alias=True)
        job = mappers.map_job_to_opencats(bundle.job).model_dump(by_alias=True)
        application = mappers.map_application_to_opencats(bundle).model_dump(by_alias=True)

        attachments: list[dict[str, Any]] = []
        if bundle.resume is not None:
            attachments.append(mappers.map_resume_to_opencats(bundle.resume).model_dump(by_alias=True))

        return {
            "candidate": candidate,
            "joborder": job,
            "candidate_joborder": application,
            "attachments": attachments,
            "endpoint": f"{self.base_url}/candidate_joborder",
        }

    def build_reconcile_payload(self, scope: str, target_id: str) -> Dict[str, Any]:
        """Return a simple payload representing a reconciliation request."""

        return {
            "scope": scope,
            "target_id": target_id,
            "endpoint": f"{self.base_url}/reconcile",
        }

    # ------------------------------------------------------------------
    def build_headers(self) -> Dict[str, str]:
        """Return authorization headers for outbound requests."""

        return {"Authorization": f"Bearer {self.api_key}"}

