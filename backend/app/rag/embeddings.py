"""
Embedding Service (Phase 4 / Phase 11 Ultra-Low Latency Vector Encoding)

Handles multi-lingual dense vector embedding generation using FastEmbed (ONNX)
or SentenceTransformers as fallback.
"""

import os
from typing import List, Optional
import numpy as np
from app.core.config import get_settings


_shared_model = None
_model_type = None  # 'fastembed' or 'sentence_transformers'
DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    """Service to load embedding model once and compute L2-normalized dense vector representations."""

    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        self.model_name = (
            model_name
            or getattr(settings, "embedding_model_name", None)
            or os.getenv("EMBEDDING_MODEL_NAME")
            or DEFAULT_MODEL_NAME
        )
        self.dimension = int(
            getattr(settings, "embedding_dimension", None)
            or os.getenv("EMBEDDING_DIMENSION", 384)
        )
        self._model = _shared_model

    def _load_model(self):
        """Pre-loads FastEmbed (ONNX) or SentenceTransformer model once into class-level singleton."""
        global _shared_model, _model_type
        if _shared_model is None:
            # Try lightweight FastEmbed ONNX Runtime first (no torch required, < 60MB RAM/disk)
            try:
                from fastembed import TextEmbedding
                _shared_model = TextEmbedding(model_name=self.model_name)
                _model_type = "fastembed"
                list(_shared_model.embed(["warmup"]))
                print(f"[EMBEDDINGS] Loaded lightweight FastEmbed ONNX model: {self.model_name}")
            except Exception as fe_err:
                print(f"[EMBEDDINGS NOTE] FastEmbed load skipped ({fe_err}), falling back to sentence_transformers...")
                try:
                    import torch
                    from sentence_transformers import SentenceTransformer
                    torch.set_num_threads(4)
                    _shared_model = SentenceTransformer(self.model_name)
                    _model_type = "sentence_transformers"
                    _shared_model.encode(sentences=["warmup"], convert_to_numpy=True, normalize_embeddings=True)
                    print(f"[EMBEDDINGS] Loaded SentenceTransformers PyTorch model: {self.model_name}")
                except Exception as st_err:
                    raise RuntimeError(f"Failed to load any embedding model: {st_err}") from st_err

            self._model = _shared_model
        else:
            self._model = _shared_model

    def encode_texts(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> np.ndarray:
        """Generates dense vector embeddings for a list of text strings."""
        if not texts:
            dim = self.dimension
            return np.empty((0, dim), dtype=np.float32)

        self._load_model()

        if _model_type == "fastembed":
            generators = self._model.embed(texts, batch_size=batch_size)
            raw = np.array(list(generators), dtype=np.float32)
            if normalize and raw.shape[0] > 0:
                norms = np.linalg.norm(raw, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                raw = raw / norms
            return raw.astype(np.float32)
        else:
            import torch
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

