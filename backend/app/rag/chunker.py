"""
Adaptive Semantic Chunker for Multilingual Text (MS MARCO-XI)

Implements semantic boundary splitting, sentence preservation, adaptive sizing,
and overlap logic for English and Indic language passages (Hindi, Marathi, Bengali, Tamil, Telugu, Urdu, etc.).
"""

import re
from typing import List, Union, Optional
from app.models.dataset import MSMarcoExample, LANGUAGE_NAME_MAP
from app.models.chunk import TextChunk


class AdaptiveSemanticChunker:
    """Adaptive semantic text chunker supporting English and Indic scripts."""

    # Sentence boundary regex including Devanagari Purna Viram (| and ||), Urdu Khatmah (۔), Urdu question mark (؟), ?, !, ., and newlines
    SENTENCE_END_PATTERN = re.compile(r'(?<=[।॥?!.\n؟۔])\s+')

    def __init__(
        self,
        target_chunk_size: int = 300,
        max_chunk_size: int = 500,
        overlap_sentences: int = 1
    ):
        """
        Initialize the chunker.

        :param target_chunk_size: Ideal character length target per chunk (~50 words)
        :param max_chunk_size: Soft maximum character length before starting a new chunk
        :param overlap_sentences: Number of trailing sentences from previous chunk to overlap
        """
        self.target_chunk_size = target_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_sentences = overlap_sentences

    def split_sentences(self, text: str) -> List[str]:
        """Splits multilingual text into sentences while respecting Devanagari, Urdu, and standard punctuation boundaries."""
        if not text or not text.strip():
            return []

        raw_sentences = self.SENTENCE_END_PATTERN.split(text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        if not sentences and text.strip():
            sentences = [text.strip()]

        return sentences

    def chunk_text(self, text: str) -> List[str]:
        """Chunks text into semantically cohesive segments using sentence boundaries."""
        sentences = self.split_sentences(text)
        if not sentences:
            return []

        chunks: List[str] = []
        current_sentences: List[str] = []
        current_len = 0

        for sentence in sentences:
            sent_len = len(sentence)

            if current_sentences and (current_len + sent_len + 1 > self.max_chunk_size):
                chunk_str = " ".join(current_sentences)
                chunks.append(chunk_str)

                if self.overlap_sentences > 0:
                    current_sentences = current_sentences[-self.overlap_sentences:]
                    current_len = sum(len(s) for s in current_sentences) + max(0, len(current_sentences) - 1)
                else:
                    current_sentences = []
                    current_len = 0

            current_sentences.append(sentence)
            current_len += sent_len + (1 if len(current_sentences) > 1 else 0)

            if current_len >= self.target_chunk_size and len(current_sentences) >= 2:
                chunk_str = " ".join(current_sentences)
                chunks.append(chunk_str)

                if self.overlap_sentences > 0:
                    current_sentences = current_sentences[-self.overlap_sentences:]
                    current_len = sum(len(s) for s in current_sentences) + max(0, len(current_sentences) - 1)
                else:
                    current_sentences = []
                    current_len = 0

        if current_sentences:
            chunk_str = " ".join(current_sentences)
            if not chunks or chunks[-1] != chunk_str:
                chunks.append(chunk_str)

        return chunks

    def chunk_passage(
        self,
        passage_text: str,
        query_id: int,
        passage_index: int,
        is_selected: int = 0,
        language_code: str = "hi",
        language_name: Optional[str] = None,
        source_lang: Optional[str] = "en",
        target_lang: Optional[str] = "hi"
    ) -> List[TextChunk]:
        """Chunks a single passage text and wraps output in TextChunk Pydantic models with explicit language metadata."""
        chunk_texts = self.chunk_text(passage_text)
        text_chunks: List[TextChunk] = []

        if not language_name and language_code:
            language_name = LANGUAGE_NAME_MAP.get(language_code.lower(), language_code)

        curr_offset = 0
        for chunk_idx, c_text in enumerate(chunk_texts):
            chunk_id = f"{query_id}_p{passage_index}_c{chunk_idx}"
            word_count = len(c_text.split())
            char_count = len(c_text)

            start_pos = passage_text.find(c_text, curr_offset)
            if start_pos == -1:
                start_pos = curr_offset
            end_pos = start_pos + char_count
            curr_offset = max(curr_offset, start_pos + 1)

            chunk_obj = TextChunk(
                chunk_id=chunk_id,
                text=c_text,
                query_id=query_id,
                passage_index=passage_index,
                chunk_index=chunk_idx,
                is_selected=is_selected,
                language_code=language_code,
                language_name=language_name,
                source_lang=source_lang,
                target_lang=target_lang,
                char_count=char_count,
                word_count=word_count,
                start_char=start_pos,
                end_char=end_pos
            )
            text_chunks.append(chunk_obj)

        return text_chunks

    def chunk_example(self, example: Union[MSMarcoExample, dict]) -> List[TextChunk]:
        """
        Chunks all translated target passages in an MSMarcoExample record, explicitly inheriting language metadata.
        """
        if isinstance(example, dict):
            example = MSMarcoExample(**example)

        query_id = example.query_id
        target_lang = example.target_lang or "hi"
        source_lang = example.source_lang or "en"
        lang_name = example.language_name or LANGUAGE_NAME_MAP.get(target_lang.lower(), target_lang)

        translated_passages = example.passages.Translated_passages
        is_selected_flags = example.passages.is_selected

        all_chunks: List[TextChunk] = []

        for p_idx, p_text in enumerate(translated_passages):
            is_sel = is_selected_flags[p_idx] if p_idx < len(is_selected_flags) else 0
            chunks = self.chunk_passage(
                passage_text=p_text,
                query_id=query_id,
                passage_index=p_idx,
                is_selected=is_sel,
                language_code=target_lang,
                language_name=lang_name,
                source_lang=source_lang,
                target_lang=target_lang
            )
            all_chunks.extend(chunks)

        return all_chunks
