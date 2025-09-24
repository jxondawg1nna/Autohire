from __future__ import annotations

import uuid
from typing import Any

from celery.utils.log import get_task_logger
from meilisearch import Client as MeilisearchClient
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from apps.shared import MiniLMEmbedder
from apps.api.app.db import Base
from apps.api.app.models import SearchDocument, SearchEmbedding

from ..config import get_settings
from ..worker import celery_app

logger = get_task_logger(__name__)
settings = get_settings()
embedder = MiniLMEmbedder(dimensions=settings.embedding_dimensions)


def _sync_database_url(url: str) -> str:
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "")
    return url


engine: Engine | None = None
try:
    from sqlalchemy import create_engine

    engine = create_engine(_sync_database_url(settings.database_url), future=True)
    Base.metadata.create_all(bind=engine)
except Exception as exc:  # pragma: no cover - defensive log for bootstrap
    logger.warning("Failed to initialize database engine for indexing tasks: %s", exc)

if engine is not None:
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
else:  # pragma: no cover - allows unit tests without database connectivity
    SessionLocal = sessionmaker()

meili_client = MeilisearchClient(settings.meilisearch_url, settings.meilisearch_api_key)
qdrant_client = QdrantClient(url=settings.qdrant_url)
_qdrant_collection_ready = False


def _ensure_qdrant_collection(vector_size: int) -> None:
    global _qdrant_collection_ready
    if _qdrant_collection_ready:
        return

    try:
        qdrant_client.get_collection(settings.qdrant_jobs_collection)
        _qdrant_collection_ready = True
        return
    except Exception:
        pass

    try:
        qdrant_client.recreate_collection(
            collection_name=settings.qdrant_jobs_collection,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )
        _qdrant_collection_ready = True
    except Exception as exc:  # pragma: no cover - remote service optional in tests
        logger.warning("Unable to prepare Qdrant collection: %s", exc)


@celery_app.task(name="autohire.search.index_job")
def index_job_document(payload: dict[str, Any]) -> str:
    """Index or update a job document across search backends."""

    document, vector = _upsert_document(payload)
    _index_meilisearch(document)
    _index_qdrant(document, vector)
    return str(document.id)


@celery_app.task(name="autohire.search.delete_job")
def delete_job_document(document_id: str) -> str:
    """Remove a job document from search backends."""

    _delete_document(document_id)
    _delete_meilisearch(document_id)
    _delete_qdrant(document_id)
    return document_id


def _upsert_document(payload: dict[str, Any]) -> tuple[SearchDocument, list[float]]:
    if engine is None:
        raise RuntimeError("Database engine is not configured for indexing tasks")
    session = SessionLocal()
    try:
        stmt = select(SearchDocument).where(SearchDocument.external_id == payload["external_id"])
        document = session.execute(stmt).scalars().first()
        if document is None:
            document = SearchDocument(
                external_id=payload["external_id"],
                document_type=payload.get("document_type", "job"),
                title=payload.get("title", ""),
                description=payload.get("description"),
                raw_text=payload.get("raw_text"),
                location=payload.get("location"),
                metadata=payload.get("metadata"),
            )
            session.add(document)
        else:
            if "title" in payload and payload["title"]:
                document.title = payload["title"]
            if "description" in payload:
                document.description = payload.get("description")
            if "raw_text" in payload:
                document.raw_text = payload.get("raw_text")
            if "location" in payload:
                document.location = payload.get("location")
            if "metadata" in payload:
                document.metadata = payload.get("metadata")

        text_for_embedding = payload.get("raw_text") or "\n".join(
            filter(None, [payload.get("title"), payload.get("description")])
        )
        vector = embedder.embed(text_for_embedding)
        embedding = next(
            (item for item in document.embeddings if item.model == settings.embedding_model_name),
            None,
        )
        if embedding:
            embedding.embedding = vector
            embedding.vector_dim = len(vector)
        else:
            document.embeddings.append(
                SearchEmbedding(
                    model=settings.embedding_model_name,
                    embedding=vector,
                    vector_dim=len(vector),
                )
            )

        session.commit()
        session.refresh(document)
        return document, vector
    finally:
        session.close()


def _index_meilisearch(document: SearchDocument) -> None:
    try:
        index = meili_client.index(settings.meilisearch_jobs_index)
        index.add_documents(
            [
                {
                    "document_id": str(document.id),
                    "id": str(document.id),
                    "external_id": document.external_id,
                    "title": document.title,
                    "description": document.description,
                    "location": document.location,
                    "metadata": document.metadata,
                }
            ]
        )
    except Exception as exc:  # pragma: no cover - external service optional
        logger.warning("Failed to index job in Meilisearch: %s", exc)


def _index_qdrant(document: SearchDocument, vector: list[float]) -> None:
    _ensure_qdrant_collection(len(vector))
    payload = {
        "document_id": str(document.id),
        "external_id": document.external_id,
        "title": document.title,
        "description": document.description,
        "location": document.location,
        "metadata": document.metadata,
    }
    try:
        qdrant_client.upsert(
            collection_name=settings.qdrant_jobs_collection,
            points=[
                qmodels.PointStruct(
                    id=str(document.id),
                    vector=vector,
                    payload=payload,
                )
            ],
        )
    except Exception as exc:  # pragma: no cover - external service optional
        logger.warning("Failed to index job in Qdrant: %s", exc)


def _delete_document(document_id: str) -> None:
    if engine is None:
        return
    session = SessionLocal()
    try:
        try:
            uuid_identifier = uuid.UUID(document_id)
        except ValueError:
            uuid_identifier = None

        if uuid_identifier is not None:
            document = session.get(SearchDocument, uuid_identifier)
            if document:
                session.delete(document)
                session.commit()
                return

        stmt = select(SearchDocument).where(SearchDocument.external_id == document_id)
        document = session.execute(stmt).scalars().first()
        if document:
            session.delete(document)
            session.commit()
    finally:
        session.close()


def _delete_meilisearch(document_id: str) -> None:
    try:
        index = meili_client.index(settings.meilisearch_jobs_index)
        index.delete_documents([document_id])
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to delete Meilisearch document %s: %s", document_id, exc)


def _delete_qdrant(document_id: str) -> None:
    try:
        qdrant_client.delete(
            collection_name=settings.qdrant_jobs_collection,
            points_selector=qmodels.PointIdsList(points=[document_id]),
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to delete Qdrant point %s: %s", document_id, exc)
