from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TemplateSection(BaseModel):
    """Structured block of text for resume sections."""

    title: str = Field(..., description="Section heading displayed on the resume")
    content: str = Field(..., description="Content template supporting {{placeholders}}")


class ResumeTemplateBase(BaseModel):
    name: str = Field(..., description="Human friendly template name")
    description: str = Field(..., description="Short summary explaining when to use the template")
    sections: list[TemplateSection] = Field(
        default_factory=list,
        description="Ordered set of sections used for resume generation",
    )
    variables: list[str] = Field(
        default_factory=list,
        description="List of supported template variables surfaced to the UI",
    )
    cover_letter_template: str | None = Field(
        default=None,
        description="Optional cover letter body associated with this template",
    )


class ResumeTemplate(ResumeTemplateBase):
    id: str = Field(..., description="Template identifier")


class ResumeTemplateCreate(ResumeTemplateBase):
    """Payload used when authoring a new resume template."""


class ResumeTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sections: list[TemplateSection] | None = None
    variables: list[str] | None = None
    cover_letter_template: str | None = None


class AutoApplyRuleBase(BaseModel):
    name: str = Field(..., description="Rule display name")
    target_role: str = Field(..., description="Primary role the rule optimizes for")
    keywords: list[str] = Field(default_factory=list, description="Keywords that should appear in the job description")
    locations: list[str] = Field(default_factory=list, description="Preferred locations for the opportunity")
    resume_template_id: str | None = Field(
        default=None,
        description="Optional resume template to render when the rule executes",
    )
    cover_letter_template_id: str | None = Field(
        default=None,
        description="Optional cover letter template to render when the rule executes",
    )
    status: Literal["active", "paused"] = Field(
        default="active",
        description="Whether the rule is eligible to run",
    )


class AutoApplyRule(AutoApplyRuleBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime | None = None


class AutoApplyRuleCreate(AutoApplyRuleBase):
    """Payload for creating an automation rule."""


class AutoApplyRuleUpdate(BaseModel):
    name: str | None = None
    target_role: str | None = None
    keywords: list[str] | None = None
    locations: list[str] | None = None
    resume_template_id: str | None = None
    cover_letter_template_id: str | None = None
    status: Literal["active", "paused"] | None = None
    last_run_at: datetime | None = None


class AutomationStep(BaseModel):
    """Granular audit step recorded during automation execution."""

    name: str
    status: Literal["pending", "running", "completed", "failed"]
    timestamp: datetime
    detail: str | None = None


class ApplicationLogEntry(BaseModel):
    id: str
    rule_id: str | None = Field(
        default=None,
        description="Rule that triggered the application run, if applicable",
    )
    job_id: str = Field(..., description="Unique job identifier used by downstream systems")
    job_title: str = Field(..., description="Title of the job that was processed")
    company: str = Field(..., description="Company associated with the job posting")
    channel: Literal["native", "playwright"] = Field(
        ..., description="Whether a first-party or scripted flow handled submission"
    )
    status: Literal["submitted", "failed", "skipped"]
    submitted_at: datetime
    audit_trail: list[AutomationStep] = Field(default_factory=list)
    notes: str | None = None


class ApplicationLogCreate(BaseModel):
    rule_id: str | None = None
    job_id: str
    job_title: str
    company: str
    channel: Literal["native", "playwright"]
    status: Literal["submitted", "failed", "skipped"] = "submitted"
    audit_trail: list[AutomationStep] = Field(default_factory=list)
    notes: str | None = None
    submitted_at: datetime | None = None
