from __future__ import annotations

import hashlib
from typing import Iterable, Sequence


class MiniLMEmbedder:
    """Lightweight deterministic stand-in for all-MiniLM-L6-v2 embeddings."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        if not text:
            return [0.0] * self.dimensions

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for index in range(self.dimensions):
            byte = digest[index % len(digest)]
            values.append((byte / 255.0) - 0.5)
        return values

    def embed_batch(self, texts: Iterable[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    def dimension(self) -> int:
        return self.dimensions


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """Compute cosine similarity between two vectors."""

    if not vec_a or not vec_b:
        return 0.0

    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be of the same dimensionality")

    sum_ab = 0.0
    sum_a_sq = 0.0
    sum_b_sq = 0.0
    for a, b in zip(vec_a, vec_b):
        sum_ab += a * b
        sum_a_sq += a * a
        sum_b_sq += b * b

    if sum_a_sq == 0 or sum_b_sq == 0:
        return 0.0

    return sum_ab / ((sum_a_sq**0.5) * (sum_b_sq**0.5))
