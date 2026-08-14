"""
Pydantic Data Models for Text Chunks and Chunk Metadata
"""

from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    """Represents a semantically chunked segment of text with provenance metadata."""
    chunk_id: str = Field(..., description="Unique identifier for chunk (e.g. '100001_p0_c0')")
    text: str = Field(..., description="The chunk text string in Hindi / Devanagari")
    query_id: int = Field(..., description="Associated MS MARCO query ID")
    passage_index: int = Field(..., description="Index of original passage within query example")
    chunk_index: int = Field(..., description="Sequence index of chunk within passage")
    is_selected: int = Field(default=0, description="Binary ground truth selection label (1=relevant, 0=not relevant)")
    char_count: int = Field(..., description="Character count of chunk text")
    word_count: int = Field(..., description="Word count of chunk text")
    start_char: int = Field(default=0, description="Start character offset in original passage")
    end_char: int = Field(default=0, description="End character offset in original passage")
