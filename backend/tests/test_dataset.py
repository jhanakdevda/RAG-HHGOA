"""
Unit Tests for MS MARCO-XI Dataset Sample and Pydantic Models
"""

import os
import json
import pytest
from app.models.dataset import MSMarcoExample, TranslationMeta, PassageData

SAMPLE_FILE_PATH = os.path.join("..", "data", "sample", "msmarco_xi_multilingual_sample.jsonl")


def get_sample_path():
    # Handle path resolution when running pytest from root or backend directory
    if os.path.exists(SAMPLE_FILE_PATH):
        return SAMPLE_FILE_PATH
    alt_path = os.path.join("data", "sample", "msmarco_xi_multilingual_sample.jsonl")
    if os.path.exists(alt_path):
        return alt_path
    legacy_path = os.path.join("..", "data", "sample", "msmarco_xi_hi_sample.jsonl")
    if os.path.exists(legacy_path):
        return legacy_path
    pytest.fail(f"Sample file not found at '{SAMPLE_FILE_PATH}'")


def test_sample_file_exists():
    """Verify that the sample dataset file exists and is non-empty."""
    path = get_sample_path()
    assert os.path.isfile(path), "Sample JSONL file does not exist"
    assert os.path.getsize(path) > 0, "Sample JSONL file is empty"


def test_sample_jsonl_parsing():
    """Verify that every line in the sample file is valid JSON."""
    path = get_sample_path()
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.strip():
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Line {i+1} failed JSON decoding: {e}")

    assert len(records) > 0, f"Expected non-zero records, found {len(records)}"


def test_pydantic_schema_validation():
    """Verify that all sample records validate cleanly against MSMarcoExample model."""
    path = get_sample_path()
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.strip():
                data = json.loads(line)
                example = MSMarcoExample(**data)

                assert example.query_id > 0, f"Invalid query_id on row {i+1}"
                assert isinstance(example.query, str) and len(example.query) > 0
                assert isinstance(example.Answer, str)
                assert isinstance(example.passages, PassageData)
                assert isinstance(example.meta, TranslationMeta)


def test_passage_structure_and_helper_methods():
    """Verify passage fields and selected passage helper method."""
    path = get_sample_path()
    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline()
        data = json.loads(first_line)
        example = MSMarcoExample(**data)

        # Check passage lists exist
        assert len(example.passages.Translated_passages) > 0
        assert len(example.passages.English_passages) > 0
        assert len(example.passages.is_selected) == len(example.passages.Translated_passages)

        # Check helper method returns list
        selected = example.passages.get_selected_passages()
        assert isinstance(selected, list)
