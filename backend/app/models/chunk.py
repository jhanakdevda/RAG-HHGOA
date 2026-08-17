"""
Pydantic Data Models for Text Chunks and Chunk Metadata
"""

from typing import Optional
from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    """Represents a semantically chunked segment of text with provenance and language metadata."""
    chunk_id: str = Field(..., description="Unique identifier for chunk (e.g. '100001_p0_c0')")
    text: str = Field(..., description="The chunk text string in target language or English")
    query_id: int = Field(..., description="Associated MS MARCO query ID")
    passage_index: int = Field(..., description="Index of original passage within query example")
    chunk_index: int = Field(..., description="Sequence index of chunk within passage")
    is_selected: int = Field(default=0, description="Binary ground truth selection label (1=relevant, 0=not relevant)")
    language_code: str = Field(default="hi", description="ISO language code of the chunk text (e.g. 'hi', 'en', 'mr', 'bn', 'ur')")
    language_name: Optional[str] = Field(default=None, description="Human-readable language name (e.g. 'Hindi', 'Marathi', 'Urdu')")
    source_lang: Optional[str] = Field(default="en", description="Source language ISO code ('en')")
    target_lang: Optional[str] = Field(default="hi", description="Target language ISO code")
    char_count: int = Field(..., description="Character count of chunk text")
    word_count: int = Field(..., description="Word count of chunk text")
    start_char: int = Field(default=0, description="Start character offset in original passage")
    end_char: int = Field(default=0, description="End character offset in original passage")
    title: Optional[str] = Field(default=None, description="Title of document or web page")
    url: Optional[str] = Field(default=None, description="URL of web document")
    domain: Optional[str] = Field(default=None, description="Domain name of web document")
    source_type: Optional[str] = Field(default="local_rag", description="Source type: 'local_rag' or 'web'")
