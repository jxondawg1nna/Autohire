from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException, Response, status

from ..models.automation import (
    ResumeTemplate,
    ResumeTemplateCreate,
    ResumeTemplateUpdate,
    TemplateSection,
)

router = APIRouter()


def _seed_templates() -> list[ResumeTemplate]:
    """Initial templates to help the frontend prototype interactions."""

    return [
        ResumeTemplate(
            id="product-story",
            name="Product Story Narrative",
            description="Balanced resume that highlights storytelling, research, and impact for product design roles.",
            sections=[
                TemplateSection(
                    title="Professional Summary",
                    content=(
                        "{{candidate.name}} is a {{candidate.yearsExperience}}-year {{candidate.title}} who "
                        "ships lovable experiences by pairing strategy with craft. Ready to support {{job.company}} as a "
                        "{{job.title}} with a bias for experimentation and measurable outcomes."
                    ),
                ),
                TemplateSection(
                    title="Core Strengths",
                    content=(
                        "Key tools and rituals: {{skills}}."
                    ),
                ),
                TemplateSection(
                    title="Recent Impact",
                    content=(
                        "Signature wins:\n{{achievements}}"
                    ),
                ),
            ],
            variables=[
                "candidate.name",
                "candidate.title",
                "candidate.yearsExperience",
                "job.company",
                "job.title",
                "skills",
                "achievements",
            ],
            cover_letter_template=(
                "Hello {{job.company}} team,\n\n"
                "I'm energized by the {{job.title}} opening and the opportunity to blend research, strategy, and craft to "
                "deliver measurable product wins. {{candidate.name}}"
            ),
        ),
        ResumeTemplate(
            id="growth-optimizer",
            name="Growth Optimizer",
            description="Data-forward resume tuned for experimentation and lifecycle marketing roles.",
            sections=[
                TemplateSection(
                    title="Mission Statement",
                    content=(
                        "Growth leader with {{candidate.yearsExperience}} years refining the full funnel. Specialized in "
                        "activation, retention, and monetization for SaaS and marketplace products."
                    ),
                ),
                TemplateSection(
                    title="Experiments That Moved Metrics",
                    content="Highlights:\n{{achievements}}",
                ),
                TemplateSection(
                    title="Toolkit",
                    content="Stacks mastered: {{skills}}.",
                ),
            ],
            variables=[
                "candidate.yearsExperience",
                "achievements",
                "skills",
            ],
            cover_letter_template=(
                "Hi there,\n\n"
                "The experimentation culture at {{job.company}} caught my eye. I'm eager to bring a hypothesis-driven mindset "
                "and a knack for cross-functional facilitation to the {{job.title}} role."
            ),
        ),
    ]


_templates_store: dict[str, ResumeTemplate] = {template.id: template for template in _seed_templates()}


@router.get("", response_model=list[ResumeTemplate])
async def list_resume_templates() -> list[ResumeTemplate]:
    """Return all resume templates."""

    return list(_templates_store.values())


@router.get("/{template_id}", response_model=ResumeTemplate)
async def get_resume_template(template_id: str) -> ResumeTemplate:
    """Retrieve a single template."""

    template = _templates_store.get(template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template


@router.post("", response_model=ResumeTemplate, status_code=status.HTTP_201_CREATED)
async def create_resume_template(payload: ResumeTemplateCreate) -> ResumeTemplate:
    """Create a new in-memory template."""

    template_id = str(uuid4())
    template = ResumeTemplate(id=template_id, **payload.model_dump())
    _templates_store[template_id] = template
    return template


@router.put("/{template_id}", response_model=ResumeTemplate)
async def update_resume_template(template_id: str, payload: ResumeTemplateUpdate) -> ResumeTemplate:
    """Update an existing template."""

    existing = _templates_store.get(template_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    update_data = payload.model_dump(exclude_unset=True)
    data = existing.model_dump()
    data.update(update_data)
    template = ResumeTemplate(**data)
    _templates_store[template_id] = template
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume_template(template_id: str) -> Response:
    """Remove a template from the in-memory store."""

    if template_id not in _templates_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    del _templates_store[template_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
