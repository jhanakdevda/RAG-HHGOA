"""
Pydantic Data Models for Multilingual Retrieval Service

Defines schemas for retrieval requests, individual search hits,
response containers with latency instrumentation, and LLM context hand-off.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.models.chunk import TextChunk


class RetrievalRequest(BaseModel):
    """Container for incoming query retrieval parameters."""
    query: str = Field(..., description="User search query in English or any supported Indic language")
    top_k: int = Field(default=5, ge=1, le=50, description="Maximum number of relevant chunks to retrieve")
    score_threshold: float = Field(default=0.0, ge=-1.0, le=1.0, description="Minimum cosine similarity score threshold")
    language_filter: Optional[str] = Field(default=None, description="Optional ISO language code to filter results (e.g. 'hi', 'mr', 'ta')")


class RetrievalResult(BaseModel):
    """Single retrieved chunk result with cosine similarity score and rank."""
    chunk: TextChunk = Field(..., description="Full text chunk with provenance and language metadata")
    score: float = Field(..., description="Cosine similarity score between query and chunk vector")
    rank: int = Field(..., description="1-based relevance rank order")


class RetrievalResponse(BaseModel):
    """Complete retrieval response with results, metadata, and latency instrumentation."""
    query: str = Field(..., description="Original input query string")
    results: List[RetrievalResult] = Field(default_factory=list, description="List of ranked retrieval results")
    total_results: int = Field(default=0, description="Number of chunks matching filters and threshold")
    latency_ms: float = Field(..., description="Total end-to-end retrieval latency in milliseconds")
    latency_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Detailed timing breakdown: query_embedding_ms, faiss_search_ms, metadata_lookup_ms"
    )
    low_confidence_warning: bool = Field(
        default=False,
        description="True if top result score fell below threshold or no results were matched"
    )

    def format_context_for_llm(self) -> str:
        """
        Consolidates retrieved chunks into a clean, formatted text block
        ready for downstream LLM Answer Generation (Phase 7).
        """
        if not self.results:
            return "No relevant context found."

        context_blocks = []
        for res in self.results:
            c = res.chunk
            lang_str = f"[{c.language_name or c.language_code}]" if c.language_code else ""
            block = f"--- Context Block {res.rank} {lang_str} (Score: {res.score:.4f}, Chunk ID: {c.chunk_id}) ---\n{c.text}"
            context_blocks.append(block)

        return "\n\n".join(context_blocks)
