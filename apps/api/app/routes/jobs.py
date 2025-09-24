from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_session
from ..models import SearchDocument
from ..schemas.search import JobLocation, JobSearchFilters, SearchHit, SearchResponse
from ..services.search import HybridSearchService

router = APIRouter()
search_service = HybridSearchService()


def _parse_filters(
    query: str,
    employment_types: list[str] | None,
    remote: bool | None,
    min_compensation: int | None,
    max_compensation: int | None,
    latitude: float | None,
    longitude: float | None,
    radius_km: float | None,
) -> JobSearchFilters:
    return JobSearchFilters(
        query=query,
        employment_types=employment_types or [],
        remote=remote,
        min_compensation=min_compensation,
        max_compensation=max_compensation,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )


@router.get("", response_model=SearchResponse)
@router.get("/search", response_model=SearchResponse, name="search_jobs")
async def search_jobs(
    session: Annotated[AsyncSession, Depends(get_session)],
    query: str = Query("", description="Keyword query used for hybrid search."),
    employment_types: list[str] | None = Query(None, alias="employmentTypes"),
    remote: bool | None = Query(None, description="Filter by remote eligibility."),
    min_compensation: int | None = Query(
        None, description="Minimum annual compensation filter in the smallest currency unit."
    ),
    max_compensation: int | None = Query(
        None, description="Maximum annual compensation filter in the smallest currency unit."
    ),
    latitude: float | None = Query(None, description="Latitude used for distance filtering."),
    longitude: float | None = Query(None, description="Longitude used for distance filtering."),
    radius_km: float | None = Query(None, description="Radius in kilometers for geo filtering."),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> SearchResponse:
    filters = _parse_filters(
        query=query,
        employment_types=employment_types,
        remote=remote,
        min_compensation=min_compensation,
        max_compensation=max_compensation,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )

    return await search_service.search_jobs(session=session, filters=filters, limit=limit, offset=offset)


@router.get("/{job_id}", response_model=SearchHit)
async def get_job(
    job_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchHit:
    document = await _get_document_by_identifier(session, job_id)
    if not document:
        raise HTTPException(status_code=404, detail="Job not found")

    location_payload = document.location or {}
    location = (
        JobLocation(
            city=location_payload.get("city"),
            region=location_payload.get("region"),
            country=location_payload.get("country"),
            latitude=location_payload.get("latitude"),
            longitude=location_payload.get("longitude"),
        )
        if location_payload
        else None
    )

    return SearchHit(
        id=str(document.id),
        external_id=document.external_id,
        title=document.title,
        description=document.description,
        location=location,
        metadata=document.metadata or {},
        score=1.0,
        highlights=None,
        distance_km=None,
        indexed_at=document.updated_at,
    )


async def _get_document_by_identifier(
    session: AsyncSession, identifier: str
) -> SearchDocument | None:
    try:
        uuid_identifier = uuid.UUID(identifier)
        document = await session.get(SearchDocument, uuid_identifier)
        if document:
            return document
    except ValueError:
        uuid_identifier = None

    stmt = select(SearchDocument).where(SearchDocument.external_id == identifier)
    result = await session.execute(stmt)
    return result.scalars().first()
