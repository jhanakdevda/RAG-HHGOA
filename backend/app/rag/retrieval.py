"""
Multilingual Retrieval Service (Optimized Phase 10 / Phase 12)

Implements dense vector query embedding, FAISS top-k similarity search,
O(1) in-memory metadata chunk lookup, language filtering, score thresholding,
low-confidence handling, and latency analytics instrumentation.
"""

import os
import json
import time
from typing import List, Optional, Dict, Set
from app.models.chunk import TextChunk
from app.models.retrieval import RetrievalRequest, RetrievalResult, RetrievalResponse
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import FAISSVectorStore

DEFAULT_FAISS_PATH = os.path.join("vector_store", "index.faiss")
DEFAULT_METADATA_PATH = os.path.join("vector_store", "chunk_metadata.jsonl")

LANG_CODE_ALIASES: Dict[str, Set[str]] = {
    "hi": {"hi", "hindi", "hin_deva"},
    "mr": {"mr", "marathi", "mar_deva"},
    "bn": {"bn", "bengali", "ben_beng"},
    "ta": {"ta", "tamil", "tam_taml"},
    "te": {"te", "telugu", "tel_telu"},
    "ur": {"ur", "urdu", "urd_arab"},
    "gu": {"gu", "gujarati", "guj_gujr"},
    "kn": {"kn", "kannada", "kan_knda"},
    "ml": {"ml", "malayalam", "mal_mlym"},
    "ne": {"ne", "nepali", "nep_deva"},
    "or": {"or", "odia", "ory_orya"},
    "pa": {"pa", "punjabi", "pan_guru"},
    "sa": {"sa", "sanskrit", "san_deva"},
    "as": {"as", "assamese", "asm_beng"},
    "en": {"en", "english"},
}


def matches_language_filter(filter_str: str, chunk: TextChunk) -> bool:
    """Checks if a chunk matches the target language filter string."""
    if not filter_str:
        return True

    clean_filter = filter_str.strip().lower()

    chunk_lang = (chunk.language_code or "").strip().lower()
    target_lang = (chunk.target_lang or "").strip().lower()
    lang_name = (chunk.language_name or "").strip().lower()

    chunk_tokens = {chunk_lang, target_lang, lang_name}

    for base_code, aliases in LANG_CODE_ALIASES.items():
        if clean_filter in aliases:
            if chunk_tokens.intersection(aliases):
                return True

    return clean_filter in chunk_tokens


class RetrievalService:
    """Core Retrieval Service wrapping EmbeddingService, FAISSVectorStore, and O(1) metadata lookup."""

    _shared_vector_store = None
    _shared_metadata_chunks: Optional[List[TextChunk]] = None

    def __init__(
        self,
        faiss_path: str = DEFAULT_FAISS_PATH,
        metadata_path: str = DEFAULT_METADATA_PATH,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[FAISSVectorStore] = None
    ):
        self.faiss_path = faiss_path
        self.metadata_path = metadata_path
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or RetrievalService._shared_vector_store

    @property
    def _metadata_cache(self) -> Optional[List[TextChunk]]:
        return RetrievalService._shared_metadata_chunks

    def _ensure_loaded(self):
        """Pre-loads FAISS index, SentenceTransformer model, and pre-instantiated TextChunk array once into RAM."""
        if self.vector_store is None or RetrievalService._shared_vector_store is None:
            f_path = self.faiss_path
            m_path = self.metadata_path

            if not os.path.exists(f_path):
                f_path = os.path.join("..", self.faiss_path)
                m_path = os.path.join("..", self.metadata_path)

            if not os.path.exists(f_path):
                raise FileNotFoundError(f"FAISS index file not found at '{self.faiss_path}' or '{f_path}'")

            store = FAISSVectorStore()
            store.load(f_path)
            RetrievalService._shared_vector_store = store
            self.vector_store = store
            self.faiss_path = f_path
            self.metadata_path = m_path

        if RetrievalService._shared_metadata_chunks is None:
            chunks = []
            m_path = self.metadata_path
            if not os.path.exists(m_path):
                m_path = os.path.join("..", self.metadata_path)

            with open(m_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        chunks.append(TextChunk(**json.loads(line)))
            RetrievalService._shared_metadata_chunks = chunks

        # Warm up embedding model weights
        self.embedding_service._load_model()

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        start_total = time.perf_counter()

        self._ensure_loaded()

        # Step 1: Query Dense Embedding
        start_embed = time.perf_counter()
        query_vec = self.embedding_service.encode_query(request.query, normalize=True)
        t_embed_ms = (time.perf_counter() - start_embed) * 1000.0

        fetch_k = max(request.top_k * 20, 100) if request.language_filter else request.top_k

        # Step 2: FAISS Vector Similarity Search
        start_faiss = time.perf_counter()
        distances, indices = self.vector_store.search(query_vec, top_k=fetch_k)
        t_faiss_ms = (time.perf_counter() - start_faiss) * 1000.0

        # Step 3: Fast O(1) Metadata Lookup & Language Filtering
        start_meta = time.perf_counter()
        results: List[RetrievalResult] = []
        low_confidence = False
        meta_chunks = RetrievalService._shared_metadata_chunks or []

        if len(distances) > 0 and len(indices) > 0:
            scores_row = distances[0]
            indices_row = indices[0]

            rank_counter = 1
            for score, idx in zip(scores_row, indices_row):
                if idx < 0 or idx >= len(meta_chunks):
                    continue

                chunk_obj = meta_chunks[idx]

                # Language filter check
                if request.language_filter and not matches_language_filter(request.language_filter, chunk_obj):
                    continue

                # Score threshold check
                float_score = float(score)
                if float_score < request.score_threshold:
                    continue

                res_item = RetrievalResult(
                    chunk=chunk_obj,
                    score=round(float_score, 4),
                    rank=rank_counter
                )
                results.append(res_item)
                rank_counter += 1

                if rank_counter > request.top_k:
                    break

        t_meta_ms = (time.perf_counter() - start_meta) * 1000.0
        t_total_ms = (time.perf_counter() - start_total) * 1000.0

        if not results or (results and results[0].score < request.score_threshold):
            low_confidence = True

        return RetrievalResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            latency_ms=round(t_total_ms, 2),
            latency_breakdown={
                "query_embedding_ms": round(t_embed_ms, 2),
                "faiss_search_ms": round(t_faiss_ms, 2),
                "metadata_lookup_ms": round(t_meta_ms, 2),
            },
            low_confidence_warning=low_confidence
        )
