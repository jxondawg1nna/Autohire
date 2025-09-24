from __future__ import annotations

import math
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from meilisearch import Client as MeilisearchClient
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..models import SearchDocument
from ..schemas.search import (
    FacetBucket,
    JobLocation,
    JobSearchFilters,
    SearchHit,
    SearchResponse,
)
from apps.shared import MiniLMEmbedder


@dataclass
class SearchCandidate:
    document_id: str
    score: float
    highlights: dict[str, Any] | None = None
    payload: dict[str, Any] | None = None


class HybridSearchService:
    """Blend keyword and semantic search results for job discovery."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.meili_index_name = "jobs"
        self.qdrant_collection = "jobs"
        self.keyword_weight = 0.5
        self.embedder = MiniLMEmbedder()
        self.meilisearch = MeilisearchClient(
            self.settings.meilisearch_url, self.settings.meilisearch_api_key
        )
        self.qdrant = QdrantClient(url=self.settings.qdrant_url)

    async def search_jobs(
        self,
        session: AsyncSession,
        filters: JobSearchFilters,
        limit: int = 25,
        offset: int = 0,
    ) -> SearchResponse:
        keyword_hits, estimated_total = self._search_meilisearch(filters, limit, offset)
        semantic_hits = self._search_qdrant(filters, limit)

        combined = self._combine_hits(keyword_hits, semantic_hits)

        documents = await self._load_documents(session, combined.keys())

        hits: list[SearchHit] = []
        facet_totals: dict[str, Counter[str]] = defaultdict(Counter)
        for document_id, candidate in combined.items():
            document = documents.get(document_id)
            if not document:
                continue

            location_payload = document.location or {}
            location = JobLocation(
                city=location_payload.get("city"),
                region=location_payload.get("region"),
                country=location_payload.get("country"),
                latitude=location_payload.get("latitude"),
                longitude=location_payload.get("longitude"),
            )
            distance_km = self._resolve_distance(filters, location)
            if (
                distance_km is not None
                and filters.radius_km is not None
                and distance_km > filters.radius_km
            ):
                continue

            metadata = document.metadata or {}
            for employment_type in metadata.get("employment_types", []) or []:
                facet_totals["employment_types"][employment_type] += 1
            if "remote" in metadata:
                facet_totals["remote"]["remote" if metadata.get("remote") else "on-site"] += 1

            hit = SearchHit(
                id=str(document.id),
                external_id=document.external_id,
                title=document.title,
                description=document.description,
                location=location,
                metadata=metadata,
                score=candidate.score,
                highlights=candidate.highlights,
                distance_km=distance_km,
                indexed_at=document.updated_at,
            )
            hits.append(hit)

        hits.sort(key=lambda item: item.score, reverse=True)

        facets = {
            name: [FacetBucket(name=facet_name, count=count) for facet_name, count in counter.items()]
            for name, counter in facet_totals.items()
        }

        total = estimated_total if estimated_total else len(hits)

        return SearchResponse(query=filters.query, total=total, hits=hits, facets=facets)

    async def _load_documents(
        self, session: AsyncSession, document_ids: Iterable[str]
    ) -> dict[str, SearchDocument]:
        document_uuid_ids = []
        for document_id in document_ids:
            try:
                document_uuid_ids.append(uuid.UUID(document_id))
            except ValueError:
                continue

        if not document_uuid_ids:
            return {}

        stmt: Select[tuple[SearchDocument]] = select(SearchDocument).where(
            SearchDocument.id.in_(document_uuid_ids)
        )
        result = await session.execute(stmt)
        documents = result.scalars().all()
        return {str(document.id): document for document in documents}

    def _search_meilisearch(
        self, filters: JobSearchFilters, limit: int, offset: int
    ) -> tuple[list[SearchCandidate], int]:
        try:
            index = self.meilisearch.index(self.meili_index_name)
            response = index.search(
                filters.query or "",
                {
                    "limit": limit,
                    "offset": offset,
                    "filter": self._build_meili_filter(filters),
                    "attributesToHighlight": ["title", "description"],
                },
            )
        except Exception:
            return [], 0

        hits: list[SearchCandidate] = []
        for item in response.get("hits", []):
            document_id = str(item.get("document_id") or item.get("id"))
            highlights = item.get("_formatted") or {}
            score = float(item.get("_rankingScore") or item.get("score") or 0.0)
            hits.append(SearchCandidate(document_id=document_id, score=score, highlights=highlights, payload=item))

        total_hits = int(
            response.get("estimatedTotalHits")
            or response.get("totalHits")
            or response.get("hitsCount")
            or len(hits)
        )
        return hits, total_hits

    def _search_qdrant(self, filters: JobSearchFilters, limit: int) -> list[SearchCandidate]:
        if not filters.query:
            return []

        query_vector = self.embedder.embed(filters.query)
        query_filter = self._build_qdrant_filter(filters)
        try:
            search_result = self.qdrant.search(
                collection_name=self.qdrant_collection,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
        except Exception:
            return []

        hits: list[SearchCandidate] = []
        for point in search_result:
            payload = point.payload or {}
            document_id = str(
                payload.get("document_id") or payload.get("id") or point.id
            )
            hits.append(SearchCandidate(document_id=document_id, score=float(point.score), payload=payload))
        return hits

    def _combine_hits(
        self, keyword_hits: list[SearchCandidate], semantic_hits: list[SearchCandidate]
    ) -> dict[str, SearchCandidate]:
        combined: dict[str, SearchCandidate] = {}

        for candidate in keyword_hits:
            combined[candidate.document_id] = candidate

        for candidate in semantic_hits:
            existing = combined.get(candidate.document_id)
            if existing:
                blended_score = (
                    self.keyword_weight * existing.score
                    + (1 - self.keyword_weight) * candidate.score
                )
                combined[candidate.document_id] = SearchCandidate(
                    document_id=candidate.document_id,
                    score=blended_score,
                    highlights=existing.highlights or candidate.highlights,
                    payload={**(existing.payload or {}), **(candidate.payload or {})},
                )
            else:
                combined[candidate.document_id] = SearchCandidate(
                    document_id=candidate.document_id,
                    score=(1 - self.keyword_weight) * candidate.score,
                    highlights=candidate.highlights,
                    payload=candidate.payload,
                )

        return combined

    def _build_meili_filter(self, filters: JobSearchFilters) -> str | None:
        clauses: list[str] = []
        if filters.remote is True:
            clauses.append("remote = true")
        elif filters.remote is False:
            clauses.append("remote = false")

        if filters.employment_types:
            escaped = ", ".join(f"'{value}'" for value in filters.employment_types)
            clauses.append(f"employment_types IN [{escaped}]")

        if filters.min_compensation is not None:
            clauses.append(f"compensation_min >= {int(filters.min_compensation)}")
        if filters.max_compensation is not None:
            clauses.append(f"compensation_max <= {int(filters.max_compensation)}")

        return " AND ".join(clauses) if clauses else None

    def _build_qdrant_filter(self, filters: JobSearchFilters) -> qmodels.Filter | None:
        conditions: list[qmodels.Condition] = []
        if filters.remote is not None:
            conditions.append(
                qmodels.FieldCondition(
                    key="remote", match=qmodels.MatchValue(value=filters.remote)
                )
            )
        if filters.employment_types:
            conditions.append(
                qmodels.FieldCondition(
                    key="employment_types", match=qmodels.MatchAny(any=filters.employment_types)
                )
            )
        if filters.min_compensation is not None:
            conditions.append(
                qmodels.FieldCondition(
                    key="compensation_min",
                    range=qmodels.Range(gte=float(filters.min_compensation)),
                )
            )
        if filters.max_compensation is not None:
            conditions.append(
                qmodels.FieldCondition(
                    key="compensation_max",
                    range=qmodels.Range(lte=float(filters.max_compensation)),
                )
            )
        if not conditions:
            return None
        return qmodels.Filter(must=conditions)

    def _resolve_distance(
        self, filters: JobSearchFilters, location: JobLocation | None
    ) -> float | None:
        if (
            filters.latitude is None
            or filters.longitude is None
            or location is None
            or location.latitude is None
            or location.longitude is None
        ):
            return None

        return self._haversine_distance(
            filters.latitude,
            filters.longitude,
            location.latitude,
            location.longitude,
        )

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        radius_km = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_km * c
