"""
Build FAISS Vector Index — Indexing script for authentic MSMARCO-XI dataset

Reads text chunks from data/processed/msmarco_xi_multilingual_chunks.jsonl,
generates 384-dimensional normalized vector embeddings using sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2,
constructs a FAISS IndexFlatIP (Cosine Similarity) index,
and persists vector_store/index.faiss and 1-to-1 vector_store/chunk_metadata.jsonl.
"""

import os
import sys
import json
import time

# Add backend directory to python path for importing app packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.chunk import TextChunk
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import FAISSVectorStore

CHUNKS_PATH = os.path.join("data", "processed", "msmarco_xi_multilingual_chunks.jsonl")
VECTOR_STORE_DIR = "vector_store"
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "chunk_metadata.jsonl")


def build_index():
    start_t = time.time()
    print("=" * 70)
    print("Building Multilingual FAISS Vector Index from Authentic Chunks")
    print("=" * 70)

    if not os.path.isfile(CHUNKS_PATH):
        print(f"Error: Processed chunks file '{CHUNKS_PATH}' does not exist. Run scripts/process_chunks.py first.")
        sys.exit(1)

    # 1. Load chunks from JSONL
    print(f"\n1. Reading chunks from '{CHUNKS_PATH}'...")
    chunks = []
    texts = []
    languages_seen = set()

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            chunk_obj = TextChunk(**data)
            chunks.append(chunk_obj)
            texts.append(chunk_obj.text)
            if chunk_obj.language_code:
                languages_seen.add(chunk_obj.language_code)

    print(f"   Loaded {len(chunks):,d} text chunks representing {len(languages_seen)} languages.")

    # 2. Generate embeddings
    print("\n2. Initializing Embedding Service (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)...")
    embedder = EmbeddingService()
    print("   Generating normalized float32 vector embeddings...")

    embeddings = embedder.encode_texts(texts, normalize=True)
    embed_dim = embedder.dimension
    print(f"   Generated matrix shape: {embeddings.shape} (dimension: {embed_dim})")

    # 3. Construct FAISS index
    print(f"\n3. Building FAISS IndexFlatIP (dimension: {embed_dim})...")
    vector_store = FAISSVectorStore(dimension=embed_dim)
    vector_store.add_vectors(embeddings)
    print(f"   Added {vector_store.ntotal:,d} vectors to FAISS index.")

    # 4. Persist Index and Metadata mapping
    print("\n4. Persisting Index and Metadata mapping to disk...")
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    vector_store.save(FAISS_INDEX_PATH)

    # Write metadata records matching vector positions 1-to-1
    with open(METADATA_PATH, "w", encoding="utf-8") as meta_f:
        for chunk in chunks:
            meta_dict = chunk.model_dump()
            meta_f.write(json.dumps(meta_dict, ensure_ascii=False) + "\n")

    # 5. Verification
    print("\n5. Verifying persisted FAISS index and metadata...")
    reloaded_store = FAISSVectorStore()
    reloaded_store.load(FAISS_INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as meta_f:
        meta_count = sum(1 for line in meta_f if line.strip())

    index_size_kb = os.path.getsize(FAISS_INDEX_PATH) / 1024
    meta_size_kb = os.path.getsize(METADATA_PATH) / 1024
    total_time = time.time() - start_t

    assert len(chunks) == reloaded_store.ntotal == meta_count, (
        f"Verification mismatch! Chunks: {len(chunks)}, FAISS vectors: {reloaded_store.ntotal}, Metadata lines: {meta_count}"
    )

    print("\n" + "=" * 70)
    print("Multilingual Vector Index Build Summary")
    print("=" * 70)
    print(f"  Embedding Model        : {embedder.model_name}")
    print(f"  Vector Dimension       : {embed_dim}")
    print(f"  Processed Chunks Read  : {len(chunks):,d}")
    print(f"  FAISS Vectors Indexed  : {reloaded_store.ntotal:,d}")
    print(f"  Metadata Lines Saved   : {meta_count:,d}")
    print(f"  Count Equality Verified: YES ({len(chunks)} == {reloaded_store.ntotal} == {meta_count})")
    print(f"  Languages Represented  : {len(languages_seen)} ({', '.join(sorted(languages_seen))})")
    print(f"  FAISS Index Type       : IndexFlatIP (Cosine Similarity)")
    print(f"  FAISS Index Path       : {FAISS_INDEX_PATH} ({index_size_kb:.2f} KB)")
    print(f"  Metadata Mapping Path  : {METADATA_PATH} ({meta_size_kb:.2f} KB)")
    print(f"  Total Build Duration   : {total_time:.2f} seconds")
    print("=" * 70)

    return reloaded_store, meta_count


if __name__ == "__main__":
    build_index()
