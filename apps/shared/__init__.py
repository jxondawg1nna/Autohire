"""Shared utilities across AutoHire services."""

from .embeddings import MiniLMEmbedder, cosine_similarity

__all__ = ["MiniLMEmbedder", "cosine_similarity"]
