"""Shared dependencies for route modules."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from ..models import EmployerContext, EmployerRole, get_employer, get_employer_member

UserIdHeader = Annotated[str, Header(alias="X-User-Id")]
EmployerIdHeader = Annotated[str | None, Header(alias="X-Employer-Id")]


async def get_current_user_id(user_id: UserIdHeader) -> str:
    """Resolve the user identifier from request headers."""

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user header")
    return user_id


async def require_employer_membership(
    employer_id: str,
    user_id: UserIdHeader,
    employer_header: EmployerIdHeader = None,
) -> EmployerContext:
    """Ensure the current user is a member of the employer scope."""

    if employer_header and employer_header != employer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employer scope mismatch between header and path.",
        )

    employer = get_employer(employer_id)
    if not employer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found.")

    member = get_employer_member(employer_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized for this employer.",
        )

    return EmployerContext(employer=employer, member=member)


def require_roles(*roles: EmployerRole):
    """Dependency ensuring the caller possesses at least one of the roles."""

    required_roles = list(roles)

    async def _checker(context: EmployerContext = Depends(require_employer_membership)) -> EmployerContext:
        if required_roles and not any(role in context.member.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role to perform this action.",
            )
        return context

    return _checker
