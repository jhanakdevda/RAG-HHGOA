"""
Unit Tests for Multilingual Foundation Compatibility (MS MARCO-XI)

Tests sentence chunking, language metadata preservation, multilingual embedding generation,
and FAISS metadata mapping across all 14 official target language configurations.
"""

import os
import json
import pytest
import numpy as np

from app.models.dataset import MSMarcoExample, LANGUAGE_NAME_MAP
from app.models.chunk import TextChunk
from app.rag.chunker import AdaptiveSemanticChunker
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import FAISSVectorStore


def test_english_sentence_chunking():
    """Verify sentence splitting for English text using standard punctuation."""
    chunker = AdaptiveSemanticChunker()
    text = "Panaji is the capital city of Goa. It is located on the Mandovi River. Have you visited?"
    sentences = chunker.split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "Panaji is the capital city of Goa."


def test_marathi_sentence_chunking():
    """Verify sentence splitting for Marathi text using Devanagari Purna Viram (|)."""
    chunker = AdaptiveSemanticChunker()
    text = "पणजी ही गोव्याची राजधानी आहे। ती मांडवी नदीच्या काठावर वसलेली आहे।"
    sentences = chunker.split_sentences(text)
    assert len(sentences) == 2
    assert sentences[0] == "पणजी ही गोव्याची राजधानी आहे।"


def test_bengali_sentence_chunking():
    """Verify sentence splitting for Bengali text using Dari (|)."""
    chunker = AdaptiveSemanticChunker()
    text = "পাণাজি গোয়ার রাজধানী। এটি মান্ডবী নদীর তীরে অবস্থিত।"
    sentences = chunker.split_sentences(text)
    assert len(sentences) == 2
    assert sentences[0] == "পাণাজি গোয়ার রাজধানী।"


def test_urdu_sentence_chunking():
    """Verify sentence splitting for Urdu text using Urdu question mark (؟) and Khatmah (۔)."""
    chunker = AdaptiveSemanticChunker()
    text = "پنجی گوا کا دارالحکومت ہے۔ کیا آپ پنجی گئے ہیں؟"
    sentences = chunker.split_sentences(text)
    assert len(sentences) == 2
    assert sentences[0] == "پنجی گوا کا دارالحکومت ہے۔"
    assert sentences[1] == "کیا آپ پنجی گئے ہیں؟"


def test_language_metadata_preservation():
    """Verify language_code, language_name, source_lang, and target_lang are preserved in TextChunk."""
    chunker = AdaptiveSemanticChunker()
    passage = "पणजी ही गोव्याची राजधानी आहे।"

    chunks = chunker.chunk_passage(
        passage_text=passage,
        query_id=501,
        passage_index=0,
        is_selected=1,
        language_code="mr",
        language_name="Marathi",
        source_lang="en",
        target_lang="mr"
    )

    assert len(chunks) == 1
    c = chunks[0]
    assert c.language_code == "mr"
    assert c.language_name == "Marathi"
    assert c.source_lang == "en"
    assert c.target_lang == "mr"


def test_multilingual_embedding_generation():
    """Verify multilingual embeddings generation for English, Hindi, Marathi, Bengali, Tamil, Telugu, Urdu."""
    service = EmbeddingService()
    multilingual_texts = [
        "Panaji is the capital of Goa.",
        "पणजी गोवा की राजधानी है।",
        "पणजी ही गोव्याची राजधानी आहे।",
        "পাণাজি গোয়ার রাজধানী।",
        "பனாஜி கோவாவின் தலைநகரம் ஆகும்.",
        "పనాజీ గోవా రాజధాని.",
        "پنجی گوا کا دارالحکومت ہے۔"
    ]

    embeddings = service.encode_texts(multilingual_texts, normalize=True)
    assert embeddings.shape == (7, 384)
    assert embeddings.dtype == np.float32

    # Check unit norms
    norms = np.linalg.norm(embeddings, axis=1)
    for norm in norms:
        assert np.isclose(norm, 1.0, atol=1e-4)


def test_faiss_multilingual_metadata_alignment():
    """Verify FAISS vector count matches chunk_metadata line count and preserves all 14 target languages."""
    faiss_path = os.path.join("..", "vector_store", "index.faiss")
    meta_path = os.path.join("..", "vector_store", "chunk_metadata.jsonl")

    if not os.path.exists(faiss_path):
        faiss_path = os.path.join("vector_store", "index.faiss")
        meta_path = os.path.join("vector_store", "chunk_metadata.jsonl")

    if not os.path.exists(faiss_path):
        pytest.skip("Persisted vector_store/index.faiss does not exist yet.")

    store = FAISSVectorStore()
    store.load(faiss_path)

    languages_found = set()
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_records = [json.loads(line) for line in f if line.strip()]

    for record in meta_records:
        if "language_code" in record:
            languages_found.add(record["language_code"])

    assert store.ntotal == len(meta_records), f"FAISS vectors ({store.ntotal}) != metadata ({len(meta_records)})"
    assert len(languages_found) == 14, f"Expected 14 target languages in metadata, found {len(languages_found)}: {languages_found}"
