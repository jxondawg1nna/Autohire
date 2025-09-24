"""Employer and team endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..models import Employer, Team, list_employers_for_user, list_teams_for_employer
from .dependencies import EmployerContext, UserIdHeader, require_roles

router = APIRouter()


@router.get("", response_model=list[Employer])
async def list_employers(user_id: UserIdHeader) -> list[Employer]:
    """Return employers the current user can access."""

    return list_employers_for_user(user_id)


@router.get("/{employer_id}", response_model=Employer)
async def get_employer_detail(
    employer_id: str,
    context: EmployerContext = Depends(require_roles()),
) -> Employer:
    """Return details for a specific employer."""

    return context.employer


@router.get("/{employer_id}/teams", response_model=list[Team])
async def get_employer_teams(
    employer_id: str,
    _context: EmployerContext = Depends(require_roles()),
) -> list[Team]:
    """List teams that belong to the employer."""

    return list_teams_for_employer(employer_id)
