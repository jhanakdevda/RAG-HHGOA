"""
Build Vector Index Script — Phase 5

Embeds Phase 4 processed text chunks using multilingual SentenceTransformer
and constructs a local FAISS IndexFlatIP vector index with 1-to-1 metadata mapping.
"""

import os
import sys
import time
import json

# Add backend directory to python path for importing app packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.chunk import TextChunk
from app.rag.embeddings import EmbeddingService, DEFAULT_MODEL_NAME
from app.rag.vector_store import FAISSVectorStore

INPUT_CHUNKS_PATH = os.path.join("data", "processed", "msmarco_xi_hi_chunks.jsonl")
FAISS_INDEX_PATH = os.path.join("vector_store", "index.faiss")
METADATA_PATH = os.path.join("vector_store", "chunk_metadata.jsonl")


def build_vector_index():
    start_time = time.time()
    print("=" * 60)
    print("Phase 5 — Building FAISS Vector Index")
    print("=" * 60)

    if not os.path.isfile(INPUT_CHUNKS_PATH):
        print(f"Error: Processed chunk file not found at '{INPUT_CHUNKS_PATH}'. Run Phase 4 first.")
        sys.exit(1)

    # 1. Load Processed Chunks & Metadata
    print(f"\n1. Reading chunks from '{INPUT_CHUNKS_PATH}'...")
    chunks = []
    metadata_records = []
    with open(INPUT_CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                chunk_obj = TextChunk(**data)
                chunks.append(chunk_obj)
                # Build 1-to-1 metadata dict preserving chunk ordering
                metadata_records.append(chunk_obj.model_dump())

    num_chunks = len(chunks)
    print(f"   Loaded {num_chunks} text chunks.")

    # 2. Initialize Embedding Model & Generate Vectors
    print(f"\n2. Initializing Embedding Service ({DEFAULT_MODEL_NAME})...")
    embedder = EmbeddingService(model_name=DEFAULT_MODEL_NAME)
    texts = [c.text for c in chunks]

    print("   Generating normalized vector embeddings...")
    embeddings = embedder.encode_texts(texts, batch_size=32, normalize=True)
    dim = embeddings.shape[1]
    print(f"   Generated embeddings matrix shape: {embeddings.shape} (dimension: {dim})")

    # 3. Create FAISS Vector Index
    print(f"\n3. Building FAISS IndexFlatIP (dimension: {dim})...")
    vector_store = FAISSVectorStore(dimension=dim)
    vector_store.add_vectors(embeddings)
    print(f"   Added {vector_store.ntotal} vectors to FAISS index.")

    # 4. Save Index and Metadata to Disk
    print("\n4. Persisting Index and Metadata mapping to disk...")
    vector_store.save(FAISS_INDEX_PATH)

    os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)
    with open(METADATA_PATH, "w", encoding="utf-8") as meta_f:
        for record in metadata_records:
            meta_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # 5. Verification Check: Load Saved Index
    print("\n5. Verifying persisted FAISS index and metadata...")
    loaded_store = FAISSVectorStore()
    loaded_store.load(FAISS_INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as meta_f:
        meta_count = sum(1 for line in meta_f if line.strip())

    assert loaded_store.ntotal == num_chunks, f"Mismatch: FAISS vectors ({loaded_store.ntotal}) != chunks ({num_chunks})"
    assert meta_count == num_chunks, f"Mismatch: Metadata lines ({meta_count}) != chunks ({num_chunks})"
    assert loaded_store.dimension == dim, f"Dimension mismatch: {loaded_store.dimension} != {dim}"

    build_duration = time.time() - start_time
    index_size_kb = os.path.getsize(FAISS_INDEX_PATH) / 1024
    meta_size_kb = os.path.getsize(METADATA_PATH) / 1024

    print("\n" + "=" * 60)
    print("Phase 5 Vector Index Build Summary")
    print("=" * 60)
    print(f"  Embedding Model        : {DEFAULT_MODEL_NAME}")
    print(f"  Runtime Vector Dimension: {dim}")
    print(f"  Processed Chunks Read  : {num_chunks}")
    print(f"  FAISS Vectors Indexed  : {loaded_store.ntotal}")
    print(f"  Metadata Lines Saved   : {meta_count}")
    print(f"  FAISS Index Type       : IndexFlatIP (Cosine Similarity)")
    print(f"  FAISS Index Path       : {FAISS_INDEX_PATH} ({index_size_kb:.2f} KB)")
    print(f"  Metadata Mapping Path  : {METADATA_PATH} ({meta_size_kb:.2f} KB)")
    print(f"  Total Build Duration   : {build_duration:.2f} seconds")
    print("=" * 60)


if __name__ == "__main__":
    build_vector_index()
