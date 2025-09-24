from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

from celery import Celery

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BACKEND_URL = CELERY_BROKER_URL

celery_app = Celery("autohire", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)
celery_app.conf.task_default_queue = "default"
celery_app.conf.result_expires = 3600

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([\w\.]+)\s*}}")


def _compose_context(candidate_profile: dict[str, Any], job_posting: dict[str, Any]) -> dict[str, Any]:
    """Merge profile and job data into a single lookup dictionary for templates."""

    context: dict[str, Any] = dict(candidate_profile)
    if "candidate" not in context:
        scalar_fields = {
            key: value
            for key, value in candidate_profile.items()
            if not isinstance(value, (list, dict))
        }
        context["candidate"] = scalar_fields
    context.setdefault("candidate", {})
    context["job"] = job_posting
    return context


def _pluck(context: dict[str, Any], dotted_key: str) -> Any:
    value: Any = context
    for part in dotted_key.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(f"• {item}" for item in value)
    return str(value)


def _render_text(template_text: str, context: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = _pluck(context, key)
        return _format_value(value)

    return PLACEHOLDER_PATTERN.sub(replace, template_text)


def _audit_event(name: str, status: str, detail: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@celery_app.task(name="autohire.echo")
def echo(message: str) -> str:
    """Simple heartbeat task for smoke testing the worker stack."""

    return message


@celery_app.task(name="autohire.generate_tailored_resume")
def generate_tailored_resume(
    template: dict[str, Any],
    candidate_profile: dict[str, Any],
    job_posting: dict[str, Any],
) -> dict[str, Any]:
    """Render resume sections using the provided template and context."""

    context = _compose_context(candidate_profile, job_posting)
    rendered_sections = []
    for section in template.get("sections", []):
        rendered_sections.append(
            {
                "title": section.get("title", ""),
                "content": _render_text(section.get("content", ""), context),
            }
        )

    return {
        "template_id": template.get("id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": rendered_sections,
        "variables_used": template.get("variables", []),
    }


@celery_app.task(name="autohire.generate_cover_letter")
def generate_cover_letter(
    template: dict[str, Any],
    candidate_profile: dict[str, Any],
    job_posting: dict[str, Any],
) -> dict[str, Any]:
    """Produce a personalized cover letter body."""

    context = _compose_context(candidate_profile, job_posting)
    cover_letter_template = template.get("cover_letter_template") or (
        "Hello {{job.company}} team,\n\n{{candidate.name}} is excited about the {{job.title}} opportunity."
    )
    body = _render_text(cover_letter_template, context)

    return {
        "template_id": template.get("id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "body": body,
    }


@celery_app.task(name="autohire.submit_application")
def submit_application(application_payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate a native or scripted application submission with audit details."""

    submission_mode = application_payload.get("submission_mode", "native")
    job = application_payload.get("job", {})
    candidate = application_payload.get("candidate", {})
    rule_id = application_payload.get("rule_id")
    audit_trail: list[dict[str, Any]] = []

    audit_trail.append(_audit_event("prepare_application", "completed", "Packaged resume and cover letter"))

    if submission_mode == "playwright":
        audit_trail.append(_audit_event("launch_browser", "completed", "Booted Chromium via Playwright"))
        if application_payload.get("simulate_failure"):
            audit_trail.append(
                _audit_event(
                    "complete_web_form",
                    "failed",
                    "Captcha challenge requires manual follow-up",
                )
            )
            status = "failed"
            notes = "Playwright automation failed due to captcha."
        else:
            audit_trail.append(_audit_event("complete_web_form", "completed", "Filed job application via scripted flow"))
            status = "submitted"
            notes = "Application submitted using Playwright automation."
    else:
        audit_trail.append(_audit_event("call_native_integration", "completed", "Submitted via ATS API"))
        status = "submitted"
        notes = "Application submitted through native integration."

    return {
        "status": status,
        "rule_id": rule_id,
        "job": job,
        "candidate": {"name": candidate.get("name"), "email": candidate.get("email")},
        "submission_mode": submission_mode,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "audit_trail": audit_trail,
        "notes": notes,
    }
