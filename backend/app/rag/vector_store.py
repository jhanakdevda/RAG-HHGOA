"""
FAISS Vector Store Abstraction

Wraps FAISS IndexFlatIP for storing and persisting dense vector embeddings.
"""

import os
from typing import Tuple, Optional
import numpy as np


class FAISSVectorStore:
    """FAISS Vector Store using Inner Product (IndexFlatIP) for L2-normalized vector search."""

    def __init__(self, dimension: Optional[int] = None):
        """
        Initialize vector store.

        :param dimension: Embedding vector dimension (e.g. 384)
        """
        self.dimension = dimension
        self.index = None
        if dimension is not None:
            self.build_index(dimension)

    def build_index(self, dimension: int):
        """Creates a FAISS IndexFlatIP instance for the specified vector dimension."""
        import faiss
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)

    @property
    def ntotal(self) -> int:
        """Returns total number of vectors in the FAISS index."""
        return self.index.ntotal if self.index is not None else 0

    def add_vectors(self, vectors: np.ndarray):
        """
        Adds 2D float32 vector matrix to the FAISS index.

        :param vectors: NumPy array of shape (N, dimension) with float32 dtype
        """
        if self.index is None:
            if vectors.ndim == 2:
                self.build_index(vectors.shape[1])
            else:
                raise ValueError("Cannot initialize FAISS index: vector matrix must be 2D.")

        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)

        if not vectors.flags['C_CONTIGUOUS']:
            vectors = np.ascontiguousarray(vectors)

        self.index.add(vectors)

    def save(self, index_path: str):
        """Saves binary FAISS index to disk."""
        import faiss
        if self.index is None:
            raise ValueError("Cannot save empty or uninitialized FAISS index.")

        os.makedirs(os.path.dirname(os.path.abspath(index_path)), exist_ok=True)
        faiss.write_index(self.index, index_path)

    def load(self, index_path: str):
        """Loads binary FAISS index from disk."""
        import faiss
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index file not found at '{index_path}'")

        self.index = faiss.read_index(index_path)
        self.dimension = self.index.d

    def search(self, query_vectors: np.ndarray, top_k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Performs inner-product search for query vectors.

        :param query_vectors: Query vector matrix of shape (N, dimension) or (dimension,)
        :param top_k: Number of top nearest neighbors to retrieve
        :return: Tuple of (distances, indices)
        """
        if self.index is None or self.ntotal == 0:
            raise ValueError("Cannot search an empty FAISS index.")

        if query_vectors.ndim == 1:
            query_vectors = np.expand_dims(query_vectors, axis=0)

        if query_vectors.dtype != np.float32:
            query_vectors = query_vectors.astype(np.float32)

        if not query_vectors.flags['C_CONTIGUOUS']:
            query_vectors = np.ascontiguousarray(query_vectors)

        distances, indices = self.index.search(query_vectors, top_k)
        return distances, indices
