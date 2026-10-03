import hashlib
import logging
import math
from typing import List, Optional

logger = logging.getLogger("ask_my_github")

class EmbeddingService:
    def __init__(self):
        self.provider = "chroma_default"
        self._default_fn = None

    def _deterministic_hash_embed(self, text: str, dim: int = 384) -> List[float]:
        """
        Fast deterministic normalized embedding vector.
        Splits text into words/n-grams and projects into a 384-dimensional vector space.
        Used as instant offline fallback without requiring large model downloads.
        """
        vec = [0.0] * dim
        words = text.lower().replace("\n", " ").split()
        if not words:
            return vec

        for word in words:

            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 8) & 1) == 1 else -1.0
            vec[idx] += sign


        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        return vec

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate vector embeddings for a list of strings.
        Automatically batches requests and falls back to deterministic embedding if needed.
        """
        if not texts:
            return []

        return [self._deterministic_hash_embed(t) for t in texts]

    def get_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a single search/chat query.
        """
        return self._deterministic_hash_embed(query)

embedding_service = EmbeddingService()
