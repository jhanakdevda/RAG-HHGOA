"""
Unit Tests for FAISSVectorStore Abstraction and Persistence
"""

import os
import json
import tempfile
import pytest
import numpy as np
from app.rag.vector_store import FAISSVectorStore


def test_faiss_vector_store_creation_and_add():
    """Verify FAISS IndexFlatIP initialization and vector addition."""
    dim = 768
    store = FAISSVectorStore(dimension=dim)
    assert store.dimension == dim
    assert store.ntotal == 0

    # Create dummy float32 normalized vectors
    vectors = np.random.randn(10, dim).astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / norms

    store.add_vectors(vectors)
    assert store.ntotal == 10


def test_faiss_save_and_load(tmp_path):
    """Verify FAISS index can be saved to disk and reloaded successfully."""
    dim = 768
    index_path = os.path.join(tmp_path, "test_index.faiss")

    store = FAISSVectorStore(dimension=dim)
    vectors = np.random.randn(15, dim).astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / norms
    store.add_vectors(vectors)

    # Save
    store.save(index_path)
    assert os.path.exists(index_path)
    assert os.path.getsize(index_path) > 0

    # Load into fresh store
    loaded_store = FAISSVectorStore()
    loaded_store.load(index_path)

    assert loaded_store.ntotal == 15
    assert loaded_store.dimension == dim


def test_faiss_search_functionality():
    """Verify vector inner product similarity search returns expected shape and distances."""
    dim = 768
    store = FAISSVectorStore(dimension=dim)
    vectors = np.random.randn(20, dim).astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / norms
    store.add_vectors(vectors)

    query = vectors[0:1]  # Vector 0 as query
    distances, indices = store.search(query, top_k=3)

    assert distances.shape == (1, 3)
    assert indices.shape == (1, 3)
    # The top match for vector 0 should be index 0 with cosine similarity ~1.0
    assert indices[0][0] == 0
    assert np.isclose(distances[0][0], 1.0, atol=1e-4)


def test_persisted_vector_store_and_metadata_integrity():
    """Verify persisted Phase 5 index and metadata files match vector count."""
    faiss_path = os.path.join("..", "vector_store", "index.faiss")
    meta_path = os.path.join("..", "vector_store", "chunk_metadata.jsonl")

    if not os.path.exists(faiss_path):
        faiss_path = os.path.join("vector_store", "index.faiss")
        meta_path = os.path.join("vector_store", "chunk_metadata.jsonl")

    if not os.path.exists(faiss_path):
        pytest.skip("Persisted vector_store/index.faiss does not exist yet (run build script first).")

    store = FAISSVectorStore()
    store.load(faiss_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta_count = sum(1 for line in f if line.strip())

    assert store.ntotal > 0
    assert store.ntotal == meta_count, f"FAISS vector count ({store.ntotal}) != metadata count ({meta_count})"
