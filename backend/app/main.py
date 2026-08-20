"""FastAPI application entry point."""

from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.models.retrieval import RetrievalRequest, RetrievalResponse
from app.models.generation import AskRequest, AskResponse
from app.models.stt import TranscribeResponse
from app.rag.retrieval import RetrievalService
from app.rag.generator import GeneratorService
from app.services.stt import SpeechToTextService

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Production CORS Configuration (Configurable via CORS_ORIGINS env)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Shared global services
_retrieval_service: Optional[RetrievalService] = None
_generator_service: Optional[GeneratorService] = None
_stt_service: Optional[SpeechToTextService] = None


def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service


def get_generator_service() -> GeneratorService:
    global _generator_service
    if _generator_service is None:
        r_service = get_retrieval_service()
        _generator_service = GeneratorService(retrieval_service=r_service)
    return _generator_service


def get_stt_service() -> SpeechToTextService:
    global _stt_service
    if _stt_service is None:
        _stt_service = SpeechToTextService()
    return _stt_service


@app.on_event("startup")
def startup_event():
    """FastAPI startup handler: pre-warms resources lazily or immediately depending on environment."""
    stt_key = settings.sarvam_api_key or os.getenv("SARVAM_API_KEY")
    if stt_key:
        print("Sarvam STT configured: YES")
    else:
        print("Sarvam STT configured: NO")

    # In cloud environments (Render 512MB RAM), defer heavy model loading to first request to allow instant port binding
    if os.getenv("RENDER") or os.getenv("DEFER_PREWARM") or settings.debug is False:
        print("[STARTUP] Fast boot enabled: Heavy model pre-warming deferred to first request for low RAM footprint.")
        return

    try:
        r_service = get_retrieval_service()
        r_service._ensure_loaded()
        prov = get_llm_provider()
        if hasattr(prov, "warm_connection"):
            prov.warm_connection()
        get_generator_service()
        print("[STARTUP] Pre-warming complete: Retrieval, FAISS, SentenceTransformer, GroundingVerifier, and LLM Provider ready.")
    except Exception as e:
        print(f"[STARTUP WARNING] Resource pre-warming deferred: {e}")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return service health status."""
    return {
        "status": "ok",
        "project": "HH Goa Voice RAG",
        "stage": "backend foundation",
    }


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_speech(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en")
) -> TranscribeResponse:
    """
    Transcribes recorded user speech audio using Sarvam STT API.
    Returns transcribed text string, detected language, and STT latency breakdown.
    """
    try:
        audio_bytes = await file.read()
        service = get_stt_service()
        return service.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=file.filename or "speech.webm",
            language_code=language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-Text transcription error: {e}")


@app.post("/retrieve", response_model=RetrievalResponse)
def retrieve_chunks(request: RetrievalRequest) -> RetrievalResponse:
    """
    Executes dense vector top-k retrieval across authentic MS MARCO-XI multilingual chunks.
    Supports query embedding, FAISS search, language filtering, score thresholding, and latency analytics.
    """
    try:
        service = get_retrieval_service()
        return service.retrieve(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Retrieval Service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {e}")


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest) -> AskResponse:
    """
    Executes end-to-end grounded RAG answer generation.
    Retrieves relevant context, constructs grounded prompt, invokes configured LLM provider,
    and returns answer with source attribution and latency breakdown.
    """
    try:
        service = get_generator_service()
        return service.generate_answer(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation error: {e}")
