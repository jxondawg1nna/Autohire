"""Microtask campaign endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..models import (
    EmployerRole,
    Microtask,
    MicrotaskCampaign,
    get_microtask_campaign,
    list_microtask_campaigns,
    list_microtasks_for_campaign,
)
from .dependencies import EmployerContext, require_roles

router = APIRouter()


@router.get("/campaigns", response_model=list[MicrotaskCampaign])
async def list_campaigns(
    employer_id: str,
    _context: EmployerContext = Depends(
        require_roles(EmployerRole.OWNER, EmployerRole.RECRUITER, EmployerRole.HIRING_MANAGER)
    ),
) -> list[MicrotaskCampaign]:
    """Return campaigns owned by the employer."""

    return list_microtask_campaigns(employer_id)


@router.get("/campaigns/{campaign_id}", response_model=MicrotaskCampaign)
async def get_campaign_detail(
    employer_id: str,
    campaign_id: str,
    _context: EmployerContext = Depends(
        require_roles(EmployerRole.OWNER, EmployerRole.RECRUITER, EmployerRole.HIRING_MANAGER)
    ),
) -> MicrotaskCampaign:
    """Return a specific campaign."""

    campaign = get_microtask_campaign(employer_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    return campaign


@router.get("/campaigns/{campaign_id}/tasks", response_model=list[Microtask])
async def list_campaign_tasks(
    employer_id: str,
    campaign_id: str,
    _context: EmployerContext = Depends(
        require_roles(
            EmployerRole.OWNER,
            EmployerRole.RECRUITER,
            EmployerRole.HIRING_MANAGER,
            EmployerRole.CONTRIBUTOR,
        )
    ),
) -> list[Microtask]:
    """Return tasks for the specified campaign."""

    campaign = get_microtask_campaign(employer_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")

    return list_microtasks_for_campaign(employer_id, campaign_id)
