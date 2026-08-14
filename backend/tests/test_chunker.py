"""
Unit Tests for AdaptiveSemanticChunker and TextChunk Models
"""

import os
import json
import pytest
from app.models.dataset import MSMarcoExample
from app.models.chunk import TextChunk
from app.rag.chunker import AdaptiveSemanticChunker

SAMPLE_FILE_PATH = os.path.join("..", "data", "sample", "msmarco_xi_hi_sample.jsonl")


def get_sample_path():
    if os.path.exists(SAMPLE_FILE_PATH):
        return SAMPLE_FILE_PATH
    alt_path = os.path.join("data", "sample", "msmarco_xi_hi_sample.jsonl")
    if os.path.exists(alt_path):
        return alt_path
    pytest.fail(f"Sample file not found at '{SAMPLE_FILE_PATH}' or '{alt_path}'")


def test_devanagari_sentence_splitting():
    """Test Devanagari Purna Viram (| and ||), question mark, and period sentence splitting."""
    chunker = AdaptiveSemanticChunker()
    text = "पणजी गोवा की राजधानी है। यह बहुत सुंदर शहर है! क्या आप वहाँ गए हैं? जय हिन्द॥"

    sentences = chunker.split_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "पणजी गोवा की राजधानी है।"
    assert sentences[1] == "यह बहुत सुंदर शहर है!"
    assert sentences[2] == "क्या आप वहाँ गए हैं?"
    assert sentences[3] == "जय हिन्द॥"


def test_chunking_preserves_sentence_integrity():
    """Verify that chunks do not cut Devanagari sentences or words in half."""
    chunker = AdaptiveSemanticChunker(target_chunk_size=100, max_chunk_size=200, overlap_sentences=0)
    text = "पणजी गोवा की राजधानी और उत्तरी गोवा जिले का मुख्यालय है। यह तिसवाड़ी तालुका में मांडवी नदी के तट पर स्थित है। पणजी 1843 से राजधानी रहा है।"

    chunks = chunker.chunk_text(text)
    assert len(chunks) >= 1
    for chunk in chunks:
        # Every chunk must end with valid sentence punctuation or be complete
        assert chunk.endswith("।") or chunk.endswith("?") or chunk.endswith("!") or chunk.endswith("॥")


def test_chunk_passage_metadata_inheritance():
    """Verify that TextChunk objects inherit query_id, passage_index, and is_selected correctly."""
    chunker = AdaptiveSemanticChunker()
    passage = "पणजी गोवा की राजधानी है। यह मांडवी नदी तट पर स्थित है।"

    chunks = chunker.chunk_passage(
        passage_text=passage,
        query_id=999,
        passage_index=2,
        is_selected=1
    )

    assert len(chunks) > 0
    c0 = chunks[0]
    assert isinstance(c0, TextChunk)
    assert c0.query_id == 999
    assert c0.passage_index == 2
    assert c0.chunk_index == 0
    assert c0.chunk_id == "999_p2_c0"
    assert c0.is_selected == 1
    assert c0.word_count > 0
    assert c0.char_count == len(c0.text)


def test_chunk_example_batch_processing():
    """Verify chunk_example processes all passages in an MSMarcoExample."""
    path = get_sample_path()
    chunker = AdaptiveSemanticChunker()

    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline()
        data = json.loads(first_line)
        example = MSMarcoExample(**data)

    chunks = chunker.chunk_example(example)
    assert len(chunks) == len(example.passages.Translated_passages)
    assert chunks[0].query_id == example.query_id
    assert chunks[0].is_selected == example.passages.is_selected[0]


def test_processed_chunk_file_validity():
    """Verify that data/processed/msmarco_xi_hi_chunks.jsonl exists and is valid."""
    proc_path = os.path.join("..", "data", "processed", "msmarco_xi_hi_chunks.jsonl")
    if not os.path.exists(proc_path):
        proc_path = os.path.join("data", "processed", "msmarco_xi_hi_chunks.jsonl")

    assert os.path.isfile(proc_path), "Processed chunk file does not exist"
    with open(proc_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) >= 100, f"Expected at least 100 chunk records, found {len(lines)}"

    # Validate first line against TextChunk model
    first_chunk = TextChunk(**json.loads(lines[0]))
    assert first_chunk.query_id > 0
    assert len(first_chunk.text) > 0
