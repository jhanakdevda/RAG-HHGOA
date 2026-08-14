# RAGE HH GOA

**Voice-Enabled Retrieval-Augmented Generation for HH Goa 2026 — Task 2**

---

## Project Description

RAGE HH GOA is a voice-enabled Retrieval-Augmented Generation (RAG) system built for the HH Goa 2026 hackathon. Users speak a question; the system transcribes it, retrieves relevant context from a knowledge base, and generates a grounded answer — with guardrails and full pipeline latency measurement.

This repository is developed **phase by phase**. Phase 1 establishes project structure and documentation only. No RAG pipeline, dataset download, or API integrations are implemented yet.

---

## HH Goa Task 2 Objective

Build a production-quality RAG system that:

1. Uses the **AI4Bharat MS MARCO-XI** dataset
2. Accepts **voice input** via **Sarvam** speech-to-text
3. Performs **vector-based retrieval** (not keyword-only search)
4. Uses **adaptive/semantic chunking** (not naive fixed-size chunking alone)
5. Orchestrates a complete RAG harness from query to final answer
6. Applies **guardrails** for irrelevant, unsupported, unsafe, and ungrounded responses
7. Measures **end-to-end latency** and reports **P50, P70, and P100** percentiles
8. Includes **evaluation and benchmarking** tools
9. Avoids hardcoded or mock answers

---

## Planned Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend  │────▶│   Backend    │────▶│  Vector Store   │
│  (Next.js)  │◀────│  (FastAPI)   │◀────│    (FAISS)      │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Sarvam STT    RAG Pipeline   LLM + Guardrails
```

| Layer | Responsibility |
|-------|----------------|
| **Frontend** | Voice capture, UI, display answers and latency |
| **Backend API** | Request routing, orchestration, configuration |
| **Voice** | Sarvam Saaras speech-to-text |
| **RAG** | Chunking, embedding, retrieval, context selection |
| **Guardrails** | Input/output safety and grounding checks |
| **Evaluation** | Benchmarks, latency stats, quality metrics |

---

## Planned Technology Stack

| Category | Technology |
|----------|------------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **RAG** | Hugging Face Datasets, Sentence Transformers, FAISS, NumPy, Pandas, scikit-learn |
| **Voice** | Sarvam Saaras |
| **Frontend** | Next.js, TypeScript, Tailwind CSS |
| **Configuration** | python-dotenv, `.env` / `.env.example` |

---

## Dataset Information

| Property | Value |
|----------|-------|
| **Dataset** | [AI4Bharat MS MARCO-XI](https://huggingface.co/datasets/ai4bharat/MS-MARCO-XI) |
| **Purpose** | Passage corpus for retrieval and question answering |
| **Storage** | `data/raw/` (gitignored), `data/processed/`, `data/sample/` |
| **Vector index** | `vector_store/` (gitignored, generated at build time) |

The full dataset will be downloaded and processed in a later phase. A small sample subset may be used for development and testing.

---

## Planned RAG Pipeline

```
Voice Input
    → Speech-to-Text (Sarvam)
    → Query Processing
    → Dataset Retrieval
    → Vector Search (FAISS)
    → Context Selection
    → LLM Answer Generation
    → Guardrails
    → Final Answer
    → Latency Measurement
```

Implementation lives under `backend/app/rag/` and is orchestrated by `backend/app/services/`.

---

## Planned Voice Pipeline

1. User records or uploads audio in the frontend
2. Audio is sent to the backend
3. Backend calls **Sarvam Saaras** for transcription
4. Transcribed text enters the RAG query pipeline

Implementation lives under `backend/app/voice/`.

---

## Planned Chunking Strategy

We will **not** rely on naive fixed-size chunking alone.

Planned approach (later phases):

- **Semantic chunking** — split on meaning boundaries (paragraphs, sections, topic shifts)
- **Adaptive sizing** — chunk length adjusts to content structure
- **Overlap strategy** — controlled overlap where needed for context continuity
- **Metadata preservation** — source IDs, titles, and position for traceability

Chunking logic will live in `backend/app/rag/`.

---

## Planned Guardrails

| Guardrail | Purpose |
|-----------|---------|
| **Irrelevant queries** | Reject or redirect off-topic questions |
| **Unsupported questions** | Detect when the corpus cannot answer |
| **Unsafe/inappropriate inputs** | Block harmful or abusive content |
| **Ungrounded answers** | Verify the LLM response is supported by retrieved context |

Implementation lives under `backend/app/guardrails/`.

---

## Planned Latency Evaluation

- Measure **complete pipeline latency** from request to final answer
- Record per-stage timings (STT, retrieval, LLM, guardrails)
- Compute **P50, P70, and P100** percentiles over benchmark runs
- Tools in `evaluation/` and `backend/app/evaluation/`

---

## Development Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **1** | Project structure and documentation | ✅ Complete |
| **2** | Backend environment setup (Python, FastAPI, deps) | ✅ Complete |
| **3** | Dataset sampling and preprocessing | ✅ Complete |
| **4** | Chunking and embedding pipeline | ✅ Complete |
| **5** | FAISS vector store build | ✅ Complete |
| **6** | RAG orchestration harness | Planned |
| **7** | Sarvam speech-to-text integration | Planned |
| **8** | LLM integration and answer generation | Planned |
| **9** | Guardrails implementation | Planned |
| **10** | Latency measurement and evaluation tools | Planned |
| **11** | Next.js frontend | Planned |
| **12** | End-to-end testing and GitHub submission prep | Planned |

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for the latest status.

---

## Local Setup Instructions

### Prerequisites

- Python 3.11+
- Git
- Node.js 24+ and npm (frontend — Phase 11+)

### Backend Setup (Windows)

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify the server is running:

- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Run backend tests:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -v
```

### Environment Variables

Copy the example file and add keys when needed in later phases:

```powershell
# From repository root
copy .env.example .env
```

| Variable | Required | Phase |
|----------|----------|-------|
| `SARVAM_API_KEY` | Later | Phase 7 (voice) |
| `LLM_API_KEY` | Later | Phase 8 (LLM) |

### Frontend (Phase 11+)

```powershell
cd frontend
npm install
npm run dev
```

---

## GitHub Submission Information

> **Placeholder — will be completed before final submission.**

- Repository: _TBD_
- Demo video: _TBD_
- Live demo URL: _TBD_
- Team members: _TBD_
- HH Goa 2026 Task 2 submission checklist: _TBD_

---

## Project Structure

```
.
├── backend/           # FastAPI application
│   ├── app/           # Application packages
│   └── tests/         # Backend tests
├── frontend/          # Next.js UI (Phase 11+)
├── data/              # Dataset storage
├── vector_store/      # FAISS index (generated)
├── scripts/           # Utility and setup scripts
├── evaluation/        # Benchmarks and reports
├── docs/              # Additional documentation
├── .env.example       # Environment variable template
├── .gitignore
├── README.md
└── PROJECT_STATUS.md
```

---

## License

_To be determined._

---

## Contributing

This is a hackathon project developed incrementally. Each phase is verified before moving to the next.
