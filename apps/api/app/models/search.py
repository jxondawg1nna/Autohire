from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from ..db.base import Base


class SearchDocument(Base):
    """Normalized representation of an entity stored in search indexes."""

    __tablename__ = "search_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[str] = mapped_column(String(64), index=True)
    document_type: Mapped[str] = mapped_column(String(32), default="job")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    location: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    embeddings: Mapped[list["SearchEmbedding"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class SearchEmbedding(Base):
    """Embedding vectors connected to a document for semantic retrieval."""

    __tablename__ = "search_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("search_documents.id", ondelete="CASCADE"), index=True
    )
    model: Mapped[str] = mapped_column(String(128))
    embedding: Mapped[list[float]] = mapped_column(JSON)
    vector_dim: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped[SearchDocument] = relationship(back_populates="embeddings")
