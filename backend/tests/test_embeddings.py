"""
Unit Tests for EmbeddingService and Multilingual Embedding Generation
"""

import pytest
import numpy as np
from app.rag.embeddings import EmbeddingService, DEFAULT_MODEL_NAME


def test_embedding_service_initialization():
    """Verify EmbeddingService initializes with default model name."""
    service = EmbeddingService()
    assert service.model_name == DEFAULT_MODEL_NAME


def test_hindi_text_embedding_generation():
    """Verify Hindi text can be embedded into a float32 NumPy matrix."""
    service = EmbeddingService()
    text = "पणजी गोवा की राजधानी है।"

    embeddings = service.encode_texts([text], normalize=True)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.dtype == np.float32
    assert embeddings.ndim == 2
    assert embeddings.shape[0] == 1
    assert embeddings.shape[1] == service.dimension


def test_embeddings_are_l2_normalized():
    """Verify output embeddings are L2 normalized (unit length)."""
    service = EmbeddingService()
    texts = [
        "पणजी गोवा की राजधानी है।",
        "दूधसागर जलप्रपात मांडवी नदी पर स्थित है।",
        "रैग प्रणाली उत्तर जनरेशन के लिए उपयोग की जाती है।"
    ]

    embeddings = service.encode_texts(texts, normalize=True)
    norms = np.linalg.norm(embeddings, axis=1)

    # Check each norm is approximately 1.0
    for norm in norms:
        assert np.isclose(norm, 1.0, atol=1e-5), f"Expected unit norm 1.0, got {norm}"


def test_multi_text_batch_encoding():
    """Verify encoding multiple texts produces matrix of shape (N, dimension)."""
    service = EmbeddingService()
    texts = [f"परीक्षण वाक्य {i}" for i in range(5)]

    embeddings = service.encode_texts(texts, batch_size=2, normalize=True)
    assert embeddings.shape == (5, service.dimension)
