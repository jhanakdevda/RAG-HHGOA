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

OFFICIALLY_SUPPORTED_LANGUAGES: Set[str] = {"en", "hi", "mr", "gu"}

LANG_CODE_ALIASES: Dict[str, Set[str]] = {
    "en": {"en", "english"},
    "hi": {"hi", "hindi", "hin_deva"},
    "mr": {"mr", "marathi", "mar_deva"},
    "gu": {"gu", "gujarati", "guj_gujr"},
    "bn": {"bn", "bengali", "ben_beng"},
    "ta": {"ta", "tamil", "tam_taml"},
    "te": {"te", "telugu", "tel_telu"},
    "ur": {"ur", "urdu", "urd_arab"},
    "kn": {"kn", "kannada", "kan_knda"},
    "ml": {"ml", "malayalam", "mal_mlym"},
    "ne": {"ne", "nepali", "nep_deva"},
    "or": {"or", "odia", "ory_orya"},
    "pa": {"pa", "punjabi", "pan_guru"},
    "sa": {"sa", "sanskrit", "san_deva"},
    "as": {"as", "assamese", "asm_beng"},
}


def detect_query_language(text: str) -> str:
    """
    Detects language code from query text using script range heuristics and language markers.
    Returns standard ISO 2-letter language code (e.g. 'en', 'hi', 'mr', 'gu', 'bn', 'ta', 'te', 'ur', 'sa').
    """
    if not text or not text.strip():
        return "en"

    clean = text.strip()

    devanagari_chars = sum(1 for c in clean if '\u0900' <= c <= '\u097f')
    gujarati_chars = sum(1 for c in clean if '\u0a80' <= c <= '\u0aff')
    bengali_chars = sum(1 for c in clean if '\u0980' <= c <= '\u09ff')
    tamil_chars = sum(1 for c in clean if '\u0b80' <= c <= '\u0bff')
    telugu_chars = sum(1 for c in clean if '\u0c00' <= c <= '\u0c7f')
    arabic_chars = sum(1 for c in clean if '\u0600' <= c <= '\u06ff')
    kannada_chars = sum(1 for c in clean if '\u0c80' <= c <= '\u0cff')
    malayalam_chars = sum(1 for c in clean if '\u0d00' <= c <= '\u0d7f')
    gurmukhi_chars = sum(1 for c in clean if '\u0a00' <= c <= '\u0a7f')

    total_len = len(clean)

    if devanagari_chars > total_len * 0.15:
        marathi_keywords = {'आहे', 'काय', 'म्हणजे', 'नाही', 'या', 'पण', 'कसे'}
        words = set(clean.split())
        if words.intersection(marathi_keywords):
            return "mr"
        return "hi"

    if gujarati_chars > total_len * 0.15:
        return "gu"
    if bengali_chars > total_len * 0.15:
        return "bn"
    if tamil_chars > total_len * 0.15:
        return "ta"
    if telugu_chars > total_len * 0.15:
        return "te"
    if arabic_chars > total_len * 0.15:
        return "ur"
    if kannada_chars > total_len * 0.15:
        return "kn"
    if malayalam_chars > total_len * 0.15:
        return "ml"
    if gurmukhi_chars > total_len * 0.15:
        return "pa"

    return "en"


def normalize_supported_language(code: Optional[str], default: Optional[str] = "en") -> Optional[str]:
    """
    Normalizes language code. Returns base code if recognized in LANG_CODE_ALIASES,
    otherwise falls back to default.
    """
    if not code or not str(code).strip():
        return default
    clean = str(code).strip().lower()
    if clean == "auto":
        return default
    for base_code, aliases in LANG_CODE_ALIASES.items():
        if clean == base_code or clean in aliases:
            return base_code
    return default


import urllib.request
import urllib.parse

_translation_cache: Dict[str, str] = {}


def translate_text_to_english(text: str) -> str:
    """Translates an Indic text passage to clean English for English query retrieval."""
    if not text or not text.strip():
        return text
    clean_text = text.strip()
    if clean_text in _translation_cache:
        return _translation_cache[clean_text]

    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q=" + urllib.parse.quote(clean_text)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, list) and len(data) > 0 and data[0]:
                translated_parts = [part[0] for part in data[0] if part and isinstance(part, list) and len(part) > 0 and part[0]]
                translated = " ".join(translated_parts).strip()
                if translated:
                    _translation_cache[clean_text] = translated
                    return translated
    except Exception:
        pass

    return clean_text


def detect_query_language(text: str) -> str:
    """
    Detects language code from query text using script range heuristics and language markers.
    Returns standard ISO 2-letter language code (e.g. 'en', 'hi', 'mr', 'gu', 'bn', 'ta', 'te', 'ur', 'sa').
    """
    if not text or not text.strip():
        return "en"

    clean = text.strip()

    devanagari_chars = sum(1 for c in clean if '\u0900' <= c <= '\u097f')
    gujarati_chars = sum(1 for c in clean if '\u0a80' <= c <= '\u0aff')
    bengali_chars = sum(1 for c in clean if '\u0980' <= c <= '\u09ff')
    tamil_chars = sum(1 for c in clean if '\u0b80' <= c <= '\u0bff')
    telugu_chars = sum(1 for c in clean if '\u0c00' <= c <= '\u0c7f')
    arabic_chars = sum(1 for c in clean if '\u0600' <= c <= '\u06ff')
    kannada_chars = sum(1 for c in clean if '\u0c80' <= c <= '\u0cff')
    malayalam_chars = sum(1 for c in clean if '\u0d00' <= c <= '\u0d7f')
    gurmukhi_chars = sum(1 for c in clean if '\u0a00' <= c <= '\u0a7f')

    total_len = len(clean)

    if devanagari_chars > total_len * 0.15:
        marathi_keywords = {'आहे', 'काय', 'म्हणजे', 'नाही', 'या', 'पण', 'कसे'}
        words = set(clean.split())
        if words.intersection(marathi_keywords):
            return "mr"
        return "hi"

    if gujarati_chars > total_len * 0.15:
        return "gu"
    if bengali_chars > total_len * 0.15:
        return "bn"
    if tamil_chars > total_len * 0.15:
        return "ta"
    if telugu_chars > total_len * 0.15:
        return "te"
    if arabic_chars > total_len * 0.15:
        return "ur"
    if kannada_chars > total_len * 0.15:
        return "kn"
    if malayalam_chars > total_len * 0.15:
        return "ml"
    if gurmukhi_chars > total_len * 0.15:
        return "pa"

    return "en"


def normalize_supported_language(code: Optional[str], default: Optional[str] = "en") -> Optional[str]:
    """
    Normalizes language code. Returns base code if recognized in LANG_CODE_ALIASES,
    otherwise falls back to default.
    """
    if not code or not str(code).strip():
        return default
    clean = str(code).strip().lower()
    if clean == "auto":
        return default
    for base_code, aliases in LANG_CODE_ALIASES.items():
        if clean == base_code or clean in aliases:
            return base_code
    return default


def matches_language_filter(filter_str: str, chunk: TextChunk) -> bool:
    """Checks if a chunk matches the target language filter string."""
    if not filter_str:
        return True

    clean_filter = filter_str.strip().lower()
    if clean_filter == "auto":
        return True

    chunk_lang = (chunk.language_code or "").strip().lower()
    target_lang = (chunk.target_lang or "").strip().lower()
    source_lang = (chunk.source_lang or "").strip().lower()
    lang_name = (chunk.language_name or "").strip().lower()

    chunk_tokens = {chunk_lang, target_lang, source_lang, lang_name}

    for base_code, aliases in LANG_CODE_ALIASES.items():
        if clean_filter == base_code or clean_filter in aliases:
            if chunk_tokens.intersection(aliases) or base_code in chunk_tokens:
                return True

    return clean_filter in chunk_tokens


import array

class RetrievalService:
    """Core Retrieval Service wrapping EmbeddingService, FAISSVectorStore, and lazy O(1) byte-offset metadata lookup."""

    _shared_vector_store = None
    _shared_metadata_offsets: Optional[array.array] = None
    _shared_metadata_path: Optional[str] = None

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
        if (
            RetrievalService._shared_vector_store is not None
            and hasattr(RetrievalService._shared_vector_store, "dimension")
            and RetrievalService._shared_vector_store.dimension != self.embedding_service.dimension
        ):
            RetrievalService._shared_vector_store = None
        self.vector_store = vector_store or RetrievalService._shared_vector_store

    @property
    def _metadata_offsets(self) -> Optional[array.array]:
        return RetrievalService._shared_metadata_offsets

    @property
    def _metadata_cache(self) -> Optional[array.array]:
        return RetrievalService._shared_metadata_offsets

    @property
    def total_chunks(self) -> int:
        offsets = RetrievalService._shared_metadata_offsets
        return len(offsets) if offsets is not None else 0

    def get_chunk_by_index(self, idx: int) -> Optional[TextChunk]:
        """Lazily reads a single TextChunk by vector index from chunk_metadata.jsonl via byte offset seek."""
        offsets = RetrievalService._shared_metadata_offsets
        m_path = RetrievalService._shared_metadata_path or self.metadata_path
        if offsets is None or idx < 0 or idx >= len(offsets):
            return None

        try:
            with open(m_path, "r", encoding="utf-8") as f:
                f.seek(offsets[idx])
                line = f.readline()
                if line and line.strip():
                    return TextChunk(**json.loads(line))
        except Exception:
            pass
        return None

    def _ensure_loaded(self):
        """Pre-loads FAISS index and builds compact byte offset index for lazy metadata lookup."""
        if (
            self.vector_store is None
            or RetrievalService._shared_vector_store is None
            or (hasattr(RetrievalService._shared_vector_store, "dimension") and RetrievalService._shared_vector_store.dimension != self.embedding_service.dimension)
        ):
            RetrievalService._shared_vector_store = None
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

        if RetrievalService._shared_metadata_offsets is None:
            m_path = self.metadata_path
            if not os.path.exists(m_path):
                m_path = os.path.join("..", self.metadata_path)

            offsets = array.array('Q')
            with open(m_path, "rb") as f:
                pos = 0
                for line in f:
                    offsets.append(pos)
                    pos += len(line)
            RetrievalService._shared_metadata_offsets = offsets
            RetrievalService._shared_metadata_path = m_path

        # Warm up embedding model weights
        self.embedding_service._load_model()

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        start_total = time.perf_counter()

        self._ensure_loaded()

        # Step 1: Query Dense Embedding
        start_embed = time.perf_counter()
        query_vec = self.embedding_service.encode_query(request.query, normalize=True)
        t_embed_ms = (time.perf_counter() - start_embed) * 1000.0

        raw_filter = request.language_filter
        if not raw_filter or raw_filter.strip().lower() == "auto":
            target_language = detect_query_language(request.query)
        else:
            target_language = normalize_supported_language(raw_filter, default="en")

        lang_names_map = {
            "en": "English", "hi": "Hindi", "mr": "Marathi", "gu": "Gujarati",
            "bn": "Bengali", "ta": "Tamil", "te": "Telugu", "ur": "Urdu",
            "kn": "Kannada", "ml": "Malayalam", "ne": "Nepali", "or": "Odia",
            "pa": "Punjabi", "sa": "Sanskrit", "as": "Assamese"
        }
        ret_lang_name = lang_names_map.get(target_language, target_language.capitalize())

        fetch_k = max(request.top_k * 30, 200)

        # Step 2: FAISS Vector Similarity Search
        start_faiss = time.perf_counter()
        distances, indices = self.vector_store.search(query_vec, top_k=fetch_k)
        t_faiss_ms = (time.perf_counter() - start_faiss) * 1000.0

        # Step 3: Fast O(1) Lazy Metadata Lookup with Two-Stage Language Filtering
        start_meta = time.perf_counter()
        results: List[RetrievalResult] = []
        low_confidence = False
        offsets = RetrievalService._shared_metadata_offsets or array.array('Q')
        total_count = len(offsets)

        def _collect_results(filter_lang: Optional[str]) -> List[RetrievalResult]:
            collected: List[RetrievalResult] = []
            if len(distances) > 0 and len(indices) > 0:
                scores_row = distances[0]
                indices_row = indices[0]
                rank_counter = 1
                seen_query_ids = set()

                for score, idx in zip(scores_row, indices_row):
                    if idx < 0 or idx >= total_count:
                        continue

                    chunk_obj = self.get_chunk_by_index(int(idx))
                    if chunk_obj is None:
                        continue

                    if filter_lang and not matches_language_filter(filter_lang, chunk_obj):
                        continue

                    # Deduplicate passage index within same query example for cleaner evidence
                    dedup_key = f"{chunk_obj.query_id}_{chunk_obj.passage_index}"
                    if dedup_key in seen_query_ids:
                        continue
                    seen_query_ids.add(dedup_key)

                    float_score = float(score)
                    if float_score < request.score_threshold:
                        continue

                    # For English queries/filters, format chunk text in clean English
                    if filter_lang == "en" or target_language == "en":
                        eng_text = translate_text_to_english(chunk_obj.text)
                        chunk_obj = chunk_obj.model_copy(update={
                            "text": eng_text,
                            "language_code": "en",
                            "language_name": "English",
                            "target_lang": "en"
                        })

                    collected.append(RetrievalResult(
                        chunk=chunk_obj,
                        score=round(float_score, 4),
                        rank=rank_counter
                    ))
                    rank_counter += 1
                    if rank_counter > request.top_k:
                        break
            return collected

        # Stage 1: Primary Language-Specific Search
        results = _collect_results(target_language)
        pref_count = len(results)
        fallback_count = 0

        # Stage 2: Multilingual Fallback if Stage 1 yields fewer than top_k results
        if len(results) < request.top_k and target_language is not None:
            fallback_results = _collect_results(None)
            if len(fallback_results) > len(results):
                fallback_count = len(fallback_results) - len(results)
                results = fallback_results

        t_meta_ms = (time.perf_counter() - start_meta) * 1000.0
        t_total_ms = (time.perf_counter() - start_total) * 1000.0

        # Print required debug logging
        print(f"QUERY LANGUAGE: {ret_lang_name}")
        print(f"RETRIEVAL LANGUAGE: {ret_lang_name}")
        print(f"PREFERRED RESULTS: {pref_count}")
        print(f"FALLBACK RESULTS: {fallback_count}")

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
