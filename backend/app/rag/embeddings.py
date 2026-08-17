"""
Embedding Service (Phase 4 / Phase 11 Ultra-Low Latency Vector Encoding)

Handles multi-lingual dense vector embedding generation using SentenceTransformers.
"""

import os
from typing import List, Optional
import numpy as np
import torch
from app.core.config import get_settings


_shared_model = None
DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    """Service to load embedding model once and compute L2-normalized dense vector representations."""

    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        self.model_name = (
            model_name
            or getattr(settings, "embedding_model_name", None)
            or os.getenv("EMBEDDING_MODEL_NAME")
            or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.dimension = int(
            getattr(settings, "embedding_dimension", None)
            or os.getenv("EMBEDDING_DIMENSION", 384)
        )
        self._model = _shared_model

    def _load_model(self):
        """Pre-loads SentenceTransformer model once into class-level singleton."""
        global _shared_model
        if _shared_model is None:
            from sentence_transformers import SentenceTransformer
            torch.set_num_threads(4)
            _shared_model = SentenceTransformer(self.model_name)
            self._model = _shared_model
            try:
                # Pre-warm model execution once
                _shared_model.encode(sentences=["warmup"], convert_to_numpy=True, normalize_embeddings=True)
            except Exception:
                pass
        else:
            self._model = _shared_model

    def encode_texts(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> np.ndarray:
        """Generates dense vector embeddings for a list of text strings with PyTorch inference mode."""
        if not texts:
            dim = self.dimension
            return np.empty((0, dim), dtype=np.float32)

        self._load_model()

        with torch.inference_mode():
            embeddings = self._model.encode(
                sentences=texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )

        return embeddings.astype(np.float32)

    def encode_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """Helper to encode a single query string into a 2D embedding array."""
        return self.encode_texts([query], batch_size=1, normalize=normalize)
