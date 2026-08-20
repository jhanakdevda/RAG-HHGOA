"""
Grounding Verification Engine (Phase 8 / Phase 12 Ultra-Low Latency Engine)

Evaluates whether generated LLM answers are context-grounded (aligned with retrieved MS MARCO-XI context)
using sentence-level content word coverage ratio and semantic embedding similarity fallback.
"""

from enum import Enum
from typing import List, Tuple, Optional, Set
import re
import numpy as np

from app.core.config import get_settings
from app.models.chunk import TextChunk
from app.models.generation import GroundingStatus
from app.rag.embeddings import EmbeddingService


STOP_WORDS: Set[str] = {
    # English
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "of", "to", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "and", "or", "but", "if", "then", "else", "that", "this", "these", "those",
    # Hindi / Devanagari
    "का", "की", "के", "है", "हैं", "था", "थी", "थे", "में", "से", "पर", "को",
    "और", "या", "ने", "भी", "ही", "कि", "यह", "वह", "जो", "एक",
    # Marathi
    "आणि", "आहे", "होते", "ना", "या", "त्या", "की", "वर", "मध्ये",
    # Bengali
    "এবং", "হয়", "আছে", "এই", "সেই", "এর", "কে", "থেকে"
}


class InternalVerificationState(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class GroundingVerifier:
    """Verifies alignment between generated LLM answer and retrieved context chunks."""

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.settings = get_settings()
        self.last_fast_path_used: bool = True

    def _split_into_sentences(self, text: str) -> List[str]:
        """Splits answer into sentences using punctuation delimiters (| || . ? ! ॥)."""
        pattern = r"[।॥.?!]"
        raw_sentences = re.split(pattern, text)
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 5]
        return sentences if sentences else [text.strip()]

    def verify(
        self,
        answer_text: str,
        context_chunks: List[TextChunk]
    ) -> Tuple[InternalVerificationState, GroundingStatus, float]:
        """
        Evaluates context alignment score for candidate answer against retrieved context chunks.

        :return: Tuple of (InternalVerificationState, GroundingStatus, grounding_score)
        """
        if not answer_text or not context_chunks:
            self.last_fast_path_used = True
            return InternalVerificationState.INSUFFICIENT_EVIDENCE, GroundingStatus.NO_CONTEXT, 0.0

        sentences = self._split_into_sentences(answer_text)

        # Extract set of all words and stems (>=4 chars) in combined retrieved context
        combined_context = " ".join([c.text for c in context_chunks])
        ctx_words = set(re.findall(r"\w+", combined_context.lower()))
        ctx_stems = {w[:4] for w in ctx_words if len(w) >= 4}

        sentence_scores = []
        unmatched_sentences = []
        unmatched_indices = []

        for idx, s in enumerate(sentences):
            all_words = set(re.findall(r"\w+", s.lower()))
            content_words = {w for w in all_words if w not in STOP_WORDS and len(w) > 1}
            target_set = content_words if content_words else all_words

            # Extract numbers/digits (e.g. 30, 55, 100) from context and answer
            ctx_digits = set(re.findall(r"\d+", combined_context))
            ans_digits = set(re.findall(r"\d+", s))

            if target_set and ctx_words:
                # Count exact word matches or prefix/stem matches (first 4 chars)
                matched_count = sum(
                    1 for w in target_set 
                    if w in ctx_words or (len(w) >= 4 and w[:4] in ctx_stems)
                )
                coverage = matched_count / len(target_set)
                jaccard = len(all_words.intersection(ctx_words)) / len(all_words.union(ctx_words)) if all_words else 0.0
                overlap_score = max(coverage, jaccard)
            else:
                overlap_score = 0.0

            # Lexical coverage fast path (>= 0.10 or shared digits or matching stem)
            has_digit_match = bool(ans_digits and ctx_digits and ans_digits.intersection(ctx_digits))
            if overlap_score >= 0.10 or has_digit_match or (target_set and any(w in ctx_words or (len(w) >= 4 and w[:4] in ctx_stems) for w in target_set)):
                sentence_scores.append((idx, max(0.65, overlap_score)))
            else:
                unmatched_sentences.append(s)
                unmatched_indices.append((idx, overlap_score))

        # Semantic fallback using EmbeddingService for cross-lingual / low-lexical unmatched sentences
        if unmatched_sentences:
            try:
                ans_vecs = self.embedding_service.encode_texts(unmatched_sentences, normalize=True)
                ctx_vecs = self.embedding_service.encode_texts([c.text for c in context_chunks], normalize=True)

                sim_matrix = np.dot(ans_vecs, ctx_vecs.T)
                max_sims = np.max(sim_matrix, axis=1)

                for (orig_idx, lexical_score), sem_sim in zip(unmatched_indices, max_sims):
                    score_val = max(float(sem_sim), lexical_score)
                    if score_val >= 0.45:
                        sentence_scores.append((orig_idx, max(0.65, round(score_val, 4))))
                    else:
                        sentence_scores.append((orig_idx, round(score_val, 4)))
                self.last_fast_path_used = False
            except Exception:
                self.last_fast_path_used = True
                for orig_idx, lexical_score in unmatched_indices:
                    score_val = 0.60 if lexical_score >= 0.15 else 0.0
                    sentence_scores.append((orig_idx, score_val))

        sentence_scores.sort(key=lambda x: x[0])
        final_scores = [s[1] for s in sentence_scores]

        avg_score = float(np.mean(final_scores)) if final_scores else 0.0
        grounding_score = round(max(0.0, min(1.0, avg_score)), 4)

        grounded_threshold = self.settings.grounding_grounded_threshold
        partial_threshold = self.settings.grounding_partial_threshold

        if grounding_score >= grounded_threshold:
            internal_state = InternalVerificationState.SUPPORTED
            public_status = GroundingStatus.GROUNDED
        elif grounding_score >= partial_threshold:
            internal_state = InternalVerificationState.INSUFFICIENT_EVIDENCE
            public_status = GroundingStatus.PARTIALLY_GROUNDED
        else:
            internal_state = InternalVerificationState.CONTRADICTED
            public_status = GroundingStatus.UNGROUNDED

        return internal_state, public_status, grounding_score
