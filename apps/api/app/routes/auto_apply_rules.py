from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Response, status

from ..models.automation import AutoApplyRule, AutoApplyRuleCreate, AutoApplyRuleUpdate

router = APIRouter()


def _seed_rules() -> list[AutoApplyRule]:
    now = datetime.now(timezone.utc)
    return [
        AutoApplyRule(
            id="design-remote",
            name="Remote Product Design Roles",
            target_role="Senior Product Designer",
            keywords=["Figma", "design system", "user research"],
            locations=["Remote", "United States"],
            resume_template_id="product-story",
            cover_letter_template_id="product-story",
            status="active",
            created_at=now,
            updated_at=now,
            last_run_at=None,
        ),
        AutoApplyRule(
            id="growth-marketing",
            name="Lifecycle & Growth Marketing",
            target_role="Lifecycle Marketing Manager",
            keywords=["experiment", "activation", "retention"],
            locations=["Hybrid", "San Francisco", "Remote"],
            resume_template_id="growth-optimizer",
            cover_letter_template_id="growth-optimizer",
            status="paused",
            created_at=now,
            updated_at=now,
            last_run_at=now,
        ),
    ]


_rules_store: dict[str, AutoApplyRule] = {rule.id: rule for rule in _seed_rules()}


@router.get("", response_model=list[AutoApplyRule])
async def list_auto_apply_rules() -> list[AutoApplyRule]:
    """Return defined automation rules."""

    return list(_rules_store.values())


@router.get("/{rule_id}", response_model=AutoApplyRule)
async def get_auto_apply_rule(rule_id: str) -> AutoApplyRule:
    rule = _rules_store.get(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.post("", response_model=AutoApplyRule, status_code=status.HTTP_201_CREATED)
async def create_auto_apply_rule(payload: AutoApplyRuleCreate) -> AutoApplyRule:
    now = datetime.now(timezone.utc)
    rule_id = str(uuid4())
    data = payload.model_dump()
    rule = AutoApplyRule(id=rule_id, created_at=now, updated_at=now, last_run_at=None, **data)
    _rules_store[rule_id] = rule
    return rule


@router.put("/{rule_id}", response_model=AutoApplyRule)
async def update_auto_apply_rule(rule_id: str, payload: AutoApplyRuleUpdate) -> AutoApplyRule:
    existing = _rules_store.get(rule_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

    update_data = payload.model_dump(exclude_unset=True)
    base = existing.model_dump()
    base.update(update_data)
    base["updated_at"] = datetime.now(timezone.utc)
    rule = AutoApplyRule(**base)
    _rules_store[rule_id] = rule
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_auto_apply_rule(rule_id: str) -> Response:
    if rule_id not in _rules_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

    del _rules_store[rule_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
