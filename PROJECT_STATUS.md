# Project Status

## Current Phase

Phase 5 — Embeddings + FAISS Vector Store (Complete)

## Completed

- Project directory structure
- Python package scaffolding with `__init__.py` files
- `.gitignore` for secrets, dependencies, and generated artifacts
- `.env.example` with API key placeholders
- `README.md` with architecture, roadmap, and setup instructions
- `PROJECT_STATUS.md` for phase tracking
- Python 3.11 virtual environment (`backend/.venv`)
- Backend requirements (`backend/requirements.txt`)
- FastAPI application (`backend/app/main.py`)
- Configuration foundation (`backend/app/core/config.py`)
- Health endpoint (`GET /health`)
- Initial backend test (`backend/tests/test_health.py`)
- MS MARCO-XI dataset access verified via HF Datasets Server API
- Hindi (`hi`) configuration inspected and scale metrics documented
- Actual dataset schema discovered and verified (10 fields)
- Development sample script created (`scripts/create_sample.py`)
- 100-record development sample generated (`data/sample/msmarco_xi_hi_sample.jsonl`)
- Pydantic dataset models created (`backend/app/models/dataset.py`)
- Dataset documentation written (`docs/DATASET.md`)
- Dataset unit tests implemented and passing (`backend/tests/test_dataset.py`)
- `TextChunk` Pydantic model implemented (`backend/app/models/chunk.py`)
- `AdaptiveSemanticChunker` implemented with Devanagari boundary rules (`backend/app/rag/chunker.py`)
- Batch chunking script created (`scripts/process_chunks.py`)
- Processed chunk dataset generated (`data/processed/msmarco_xi_hi_chunks.jsonl`)
- Chunking documentation written (`docs/CHUNKING.md`)
- Phase 4 chunker unit tests implemented and passing (`backend/tests/test_chunker.py`)
- Multilingual embedding service integrated (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions)
- FAISS `IndexFlatIP` vector store abstraction built (`backend/app/rag/vector_store.py`)
- Vector index build script created (`scripts/build_vector_index.py`)
- FAISS binary index generated and persisted (`vector_store/index.faiss`, 300 vectors)
- 1-to-1 chunk metadata mapping generated (`vector_store/chunk_metadata.jsonl`, 300 records)
- Embeddings and Vector Store documentation written (`docs/EMBEDDINGS_AND_VECTOR_INDEX.md`)
- Phase 5 unit tests implemented and passing (`backend/tests/test_embeddings.py`, `backend/tests/test_vector_store.py`)

## Currently Working

- Phase 5 complete — awaiting confirmation before Phase 6

## Next Phase

Phase 6 — Retrieval Harness

## Known Issues

None

## Important Decisions

- Python 3.11
- FastAPI backend
- Next.js frontend
- FAISS initially for vector search
- Sarvam for speech-to-text
- MS MARCO-XI as the dataset
- Adaptive/semantic chunking (not naive fixed-size chunking)
- Guardrails for irrelevant, unsupported, unsafe, and ungrounded responses
- P50, P70, and P100 latency measurement
