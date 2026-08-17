"""
Expanded Authentic MS MARCO-XI Ground-Truth Dataset Builder (Phase 9 Optimization)

Extracts 100 authentic ground-truth records per language (14 Indic target languages) where at least one passage
has `is_selected == 1`. Chunks passages using AdaptiveSemanticChunker, embeds vectors, and updates vector_store.
"""

import os
import sys
import json
import pyarrow.parquet as pq
from typing import List, Dict

# Force UTF-8 stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.dataset import MSMarcoExample, LANGUAGE_NAME_MAP
from app.models.chunk import TextChunk
from app.rag.chunker import AdaptiveSemanticChunker
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import FAISSVectorStore

RAW_DIR = os.path.join("data", "raw", "validation")
EXPANDED_SAMPLE_PATH = os.path.join("data", "sample", "msmarco_xi_expanded_sample.jsonl")
EXPANDED_CHUNKS_PATH = os.path.join("data", "processed", "msmarco_xi_expanded_chunks.jsonl")
VECTOR_STORE_DIR = "vector_store"

PARQUET_FILES = {
    "as": "asmval.parquet",
    "bn": "benval.parquet",
    "gu": "gujval.parquet",
    "hi": "hinval.parquet",
    "kn": "kanval.parquet",
    "ml": "malval.parquet",
    "mr": "marval.parquet",
    "ne": "nepval.parquet",
    "or": "orival.parquet",
    "pa": "panval.parquet",
    "sa": "sanval.parquet",
    "ta": "tamval.parquet",
    "te": "telval.parquet",
    "ur": "urdval.parquet",
}


def build_expanded_dataset(records_per_lang: int = 100):
    print("=" * 90)
    print(f"Building Expanded Authentic MS MARCO-XI Ground-Truth Dataset ({records_per_lang} GT records/lang)")
    print("=" * 90)

    extracted_examples: List[MSMarcoExample] = []

    for lang_code, filename in PARQUET_FILES.items():
        filepath = os.path.join(RAW_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: File not found: {filepath}")
            continue

        print(f"Processing {filename} ({lang_code})...", end=" ", flush=True)
        table = pq.read_table(filepath)
        df = table.to_pandas()

        lang_count = 0
        for idx, row in df.iterrows():
            passages = row["passages"]
            is_selected = list(passages.get("is_selected", []))

            # Strictly filter for records with explicit ground-truth selected passages (is_selected == 1)
            if 1 not in is_selected:
                continue

            eng_passages = list(passages.get("English_passages", []))
            trans_passages = list(passages.get("Translated_passages", []))

            example = MSMarcoExample(
                query_id=int(row["query_id"]),
                query_type=str(row.get("query_type", "description")),
                source_lang=str(row.get("source_lang", "en")),
                target_lang=lang_code,
                language_name=LANGUAGE_NAME_MAP.get(lang_code, lang_code),
                query=str(row["query"]),
                Answer=str(row.get("Answer", "")),
                Eng_Query=str(row.get("Eng_Query", "")),
                Eng_Answer=str(row.get("Eng_Answer", "")),
                passages={
                    "English_passages": eng_passages,
                    "Translated_passages": trans_passages,
                    "is_selected": is_selected
                }
            )

            extracted_examples.append(example)
            lang_count += 1
            if lang_count >= records_per_lang:
                break

        print(f"Extracted {lang_count} ground-truth records.")

    # Save expanded sample JSONL
    os.makedirs(os.path.dirname(EXPANDED_SAMPLE_PATH), exist_ok=True)
    with open(EXPANDED_SAMPLE_PATH, "w", encoding="utf-8") as f:
        for ex in extracted_examples:
            f.write(ex.model_dump_json() + "\n")

    print(f"\nSaved {len(extracted_examples)} ground-truth examples to '{EXPANDED_SAMPLE_PATH}'.")

    if os.path.exists(EXPANDED_SAMPLE_PATH) and os.path.exists(EXPANDED_CHUNKS_PATH):
        print(f"Loading pre-extracted chunks from '{EXPANDED_CHUNKS_PATH}'...", flush=True)
        all_chunks = []
        with open(EXPANDED_CHUNKS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_chunks.append(TextChunk(**json.loads(line)))
        print(f"Loaded {len(all_chunks)} chunks.")
    else:
        # Step B: Chunking through AdaptiveSemanticChunker
        print("\nChunking passages with AdaptiveSemanticChunker...", flush=True)
        chunker = AdaptiveSemanticChunker()
        all_chunks = []

        for ex in extracted_examples:
            chunks = chunker.chunk_example(ex)
            all_chunks.extend(chunks)

        os.makedirs(os.path.dirname(EXPANDED_CHUNKS_PATH), exist_ok=True)
        with open(EXPANDED_CHUNKS_PATH, "w", encoding="utf-8") as f:
            for c in all_chunks:
                f.write(c.model_dump_json() + "\n")

        print(f"Generated {len(all_chunks)} text chunks saved to '{EXPANDED_CHUNKS_PATH}'.")

    # Step C: Re-embedding & Vector Store Indexing
    print("\nEmbedding chunks and building FAISS vector index...", flush=True)
    embedder = EmbeddingService()
    chunk_texts = [c.text for c in all_chunks]
    embeddings = embedder.encode_texts(chunk_texts, batch_size=32)

    vector_store = FAISSVectorStore(dimension=embedder.dimension)
    vector_store.add_vectors(embeddings)

    index_path = os.path.join(VECTOR_STORE_DIR, "index.faiss")
    meta_path = os.path.join(VECTOR_STORE_DIR, "chunk_metadata.jsonl")

    vector_store.save(index_path)

    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(c.model_dump_json() + "\n")

    print(f"FAISS vector store updated! {vector_store.ntotal} vectors indexed in '{index_path}'.")
    print("=" * 90)


if __name__ == "__main__":
    build_expanded_dataset(records_per_lang=100)
