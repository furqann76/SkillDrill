import numpy as np


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def is_near_duplicate(
    embedding: list[float],
    existing_embeddings: list[list[float]],
    threshold: float,
) -> bool:
    return any(
        cosine_similarity(embedding, existing) >= threshold for existing in existing_embeddings
    )
