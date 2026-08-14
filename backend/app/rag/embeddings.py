"""
Multilingual Text Embedding Service

Generates dense vector embeddings using SentenceTransformers for multilingual text,
including Hindi / Devanagari script.
"""

from typing import List, Optional
import numpy as np


DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    """Embedding service wrapping SentenceTransformer with L2 normalization and batch encoding."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        Initialize the embedding service.

        :param model_name: Hugging Face model identifier for SentenceTransformer
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy loads the SentenceTransformer model when needed."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                raise RuntimeError(f"Failed to load embedding model '{self.model_name}': {e}") from e

    @property
    def dimension(self) -> int:
        """Returns runtime embedding vector dimension of the loaded model."""
        self._load_model()
        if hasattr(self._model, "get_embedding_dimension"):
            return self._model.get_embedding_dimension()
        return self._model.get_sentence_embedding_dimension()

    def encode_texts(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generates dense vector embeddings for a list of text strings.

        :param texts: List of text strings to embed
        :param batch_size: Batch size for encoding
        :param normalize: If True, L2-normalizes vectors so inner product equals cosine similarity
        :return: NumPy array of shape (N, dimension) with dtype float32
        """
        if not texts:
            dim = self.dimension
            return np.empty((0, dim), dtype=np.float32)

        self._load_model()

        embeddings = self._model.encode(
            inputs=texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )

        embeddings = embeddings.astype(np.float32)

        # Fallback manual L2 normalization check
        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            embeddings = embeddings / norms

        return embeddings

    def encode_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """Helper to encode a single query string into a 1D or 2D embedding array."""
        arr = self.encode_texts([query], normalize=normalize)
        return arr
