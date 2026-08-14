# Multilingual Embeddings and FAISS Vector Index Documentation

**Module**: `backend/app/rag/embeddings.py` (`EmbeddingService`)  
**Vector Store**: `backend/app/rag/vector_store.py` (`FAISSVectorStore`)  
**Build Script**: `scripts/build_vector_index.py`  
**FAISS Binary Index Path**: `vector_store/index.faiss`  
**Metadata Mapping Path**: `vector_store/chunk_metadata.jsonl`

---

## 1. Embedding Model Selection

We use **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** for generating dense vector representations of Hindi/Devanagari text.

### Rationale
- **Multilingual Support**: Pretrained on 50+ languages, including Hindi and English.
- **Runtime Vector Dimension**: 384 dimensions.
- **Efficiency**: Lightweight MiniLM architecture (~470MB download, 12 layers) optimized for CPU inference.
- **Normalization**: Vectors are L2-normalized ($\|v\|_2 = 1.0$) upon output.

---

## 2. FAISS Vector Store Architecture

### Index Type: `faiss.IndexFlatIP`
- We use **Inner Product (`IndexFlatIP`)** search.
- Because vectors are L2-normalized ($A \cdot B = \frac{A \cdot B}{\|A\| \|B\|}$), Inner Product search in FAISS produces **exact Cosine Similarity**.

### 1-to-1 Metadata Mapping
FAISS binary indices do not store arbitrary dictionary metadata. We maintain a 1-to-1 position mapping in `vector_store/chunk_metadata.jsonl`:

```text
FAISS Vector Index 0 ──▶ Line 0 in vector_store/chunk_metadata.jsonl
FAISS Vector Index 1 ──▶ Line 1 in vector_store/chunk_metadata.jsonl
FAISS Vector Index N ──▶ Line N in vector_store/chunk_metadata.jsonl
```

Each metadata line retains the original provenance from Phase 4:
- `chunk_id`
- `query_id`
- `passage_index`
- `chunk_index`
- `is_selected`
- `start_char`
- `end_char`
- `text`

---

## 3. Persistence Layout

```
vector_store/
├── index.faiss            # FAISS binary index (IndexFlatIP, 384 dimensions)
└── chunk_metadata.jsonl   # 1-to-1 JSONL metadata mapping
```

---

## 4. Verification Metrics

Running `python scripts/build_vector_index.py` on the 300 processed chunks yields:

- **Model Used**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Embedding Dimension**: 384
- **Chunks Embedded**: 300
- **FAISS Vectors Indexed**: 300
- **Metadata Records Saved**: 300
- **Verification Rule**: `processed chunks == FAISS vectors == metadata records == 300`
