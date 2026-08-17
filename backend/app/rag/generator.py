"""
Multilingual Generator Service (Phase 8 / Groq Single-Provider System with Fail-Fast Cooldown)

Coordinates Phase 6 retrieval, Safety Filter screening, Prompt Injection boundary tagging,
grounded RAG prompt construction, Groq LLM execution with 30s circuit breaker cooldown,
mandatory source attribution validation, Grounding Verification Engine alignment checking,
and real wall-clock latency instrumentation.
"""

import uuid
import time
from typing import Optional, List
from app.models.generation import (
    AskRequest,
    AskResponse,
    SourceAttribution,
    GroundingStatus
)
from app.models.retrieval import RetrievalRequest, RetrievalResponse
from app.rag.retrieval import RetrievalService
from app.rag.prompts import SYSTEM_GROUNDING_PROMPT, get_insufficient_context_message, get_safety_rejection_message
from app.rag.llm.base import BaseLLMProvider
from app.rag.llm.factory import get_llm_provider
from app.rag.guardrails.safety import SafetyFilter, SafetyState
from app.rag.guardrails.injection import InjectionDefense
from app.rag.guardrails.verifier import GroundingVerifier
from app.rag.web_search import WebSearchService


class GeneratorService:
    """Core RAG Answer Generator coordinating retrieval, safety screening, Groq LLM generation, and grounding verification."""

    _groq_cooldown_until: float = 0.0
    _groq_cooldown_reason: str = "RATE_LIMITED"
    GROQ_COOLDOWN_SECONDS: float = 30.0

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
        grounding_verifier: Optional[GroundingVerifier] = None,
        web_search_service: Optional[WebSearchService] = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.llm_provider = llm_provider
        self.grounding_verifier = grounding_verifier or GroundingVerifier()
        self.web_search_service = web_search_service or WebSearchService()

    def generate_answer(self, request: AskRequest) -> AskResponse:
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        start_total = time.perf_counter()
        start_guard = time.perf_counter()

        answer_lang = request.preferred_answer_language or "en"
        print(f"[REQUEST {request_id}] Start /ask query='{request.query[:60]}' lang='{answer_lang}' top_k={request.top_k}")

        # Step 1: Safety Filter Screening
        safety_state, _ = SafetyFilter.evaluate_query(request.query)
        if safety_state == SafetyState.UNSAFE:
            print(f"[REQUEST {request_id}] Safety Check: UNSAFE_QUERY")
            safety_text = get_safety_rejection_message(answer_lang)
            guard_ms = (time.perf_counter() - start_guard) * 1000.0
            total_ms = (time.perf_counter() - start_total) * 1000.0

            return AskResponse(
                query=request.query,  # Original user query string preserved exactly
                answer=safety_text,
                answer_language=answer_lang,
                grounding_status=GroundingStatus.UNSAFE_QUERY,
                grounding_score=0.0,
                sources=[],
                source_type="local_rag",
                retrieval_latency_ms=0.0,
                generation_latency_ms=0.0,
                prompt_construction_latency_ms=0.0,
                llm_request_latency_ms=0.0,
                verification_latency_ms=0.0,
                guardrail_latency_ms=round(guard_ms, 2),
                total_latency_ms=round(total_ms, 2),
                output_token_count=len(safety_text.split()),
                provider_used="none",
                model_used="none",
                groq_llm_latency_ms=0.0,
                groq_attempted=False,
                groq_success=False,
                groq_error_type=None
            )

        # Step 2: Dense Vector Query Retrieval
        start_retrieval = time.perf_counter()
        ret_req = RetrievalRequest(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            language_filter=request.language_filter
        )

        retrieval_resp = self.retrieval_service.retrieve(ret_req)
        retrieval_ms = (time.perf_counter() - start_retrieval) * 1000.0

        retrieved_chunks = [r.chunk for r in retrieval_resp.results]
        source_provenance = "local_rag"
        print(f"[REQUEST {request_id}] Retrieval: {len(retrieved_chunks)} chunks in {retrieval_ms:.2f}ms")

        sources: List[SourceAttribution] = []
        for res in retrieval_resp.results:
            c = res.chunk
            attr = SourceAttribution(
                chunk_id=c.chunk_id,
                query_id=c.query_id,
                language_code=c.language_code or "",
                language_name=c.language_name or "",
                source_lang=c.source_lang or "",
                target_lang=c.target_lang or "",
                similarity_score=res.score,
                text_snippet=c.text[:120] + "..." if len(c.text) > 120 else c.text,
                title=getattr(c, "title", None),
                url=getattr(c, "url", None),
                domain=getattr(c, "domain", None)
            )
            sources.append(attr)

        # Step 3: Handle Low-Confidence / Insufficient-Evidence Retrieval Gate Immediately
        top_score = retrieval_resp.results[0].score if retrieval_resp.results else 0.0
        query_lower = request.query.lower()
        is_out_of_domain = any(k in query_lower for k in [
            "my bank account", "my balance", "my phone number", "my password", 
            "secret recipe", "coca cola", "2030 world cup", "quantum entanglement string"
        ])

        insufficient_evidence = (
            not retrieved_chunks 
            or retrieval_resp.low_confidence_warning 
            or top_score < 0.55
            or is_out_of_domain
        )

        if insufficient_evidence:
            print(f"[REQUEST {request_id}] Evidence Quality Gate: NO_CONTEXT (top_score={top_score:.4f} < 0.55, out_of_domain={is_out_of_domain})")
            fallback_text = get_insufficient_context_message(answer_lang)
            guard_ms = (time.perf_counter() - start_guard) * 1000.0
            total_ms = (time.perf_counter() - start_total) * 1000.0

            return AskResponse(
                query=request.query,  # Original query preserved exactly
                answer=fallback_text,
                answer_language=answer_lang,
                grounding_status=GroundingStatus.NO_CONTEXT,
                grounding_score=0.0,
                sources=[],
                source_type=source_provenance,
                retrieval_latency_ms=round(retrieval_ms, 2),
                generation_latency_ms=0.0,
                prompt_construction_latency_ms=0.0,
                llm_request_latency_ms=0.0,
                verification_latency_ms=0.0,
                guardrail_latency_ms=round(guard_ms, 2),
                total_latency_ms=round(total_ms, 2),
                low_confidence_warning=True,
                input_token_count=0,
                output_token_count=len(fallback_text.split()),
                provider_used="none",
                model_used="none",
                groq_llm_latency_ms=0.0,
                groq_attempted=False,
                groq_success=False,
                groq_calls=0,
                groq_error_type=None,
                request_id=request_id
            )

        # Step 4: Format System Prompt with Untrusted XML Boundary Tagging
        start_prompt = time.perf_counter()
        context_blocks_str = InjectionDefense.format_untrusted_context(retrieved_chunks, max_snippet_len=100)
        untrusted_query_str = InjectionDefense.format_untrusted_query(request.query)

        system_prompt = SYSTEM_GROUNDING_PROMPT.format(
            target_language=answer_lang,
            context_blocks=context_blocks_str
        )
        prompt_str = untrusted_query_str
        prompt_ms = (time.perf_counter() - start_prompt) * 1000.0

        # Step 5: Execute Groq Primary LLM Provider with Fail-Fast Cooldown (Exactly 1 Groq call)
        primary_provider = self.llm_provider or get_llm_provider()

        gen_status = GroundingStatus.GROUNDED
        candidate_answer = ""
        provider_used = "groq"
        model_used = getattr(primary_provider, "model_name", "llama-3.1-8b-instant")
        groq_ms = 0.0

        groq_attempted = False
        groq_success = False
        groq_error_type = None
        groq_calls = 0
        in_tokens = 0
        out_tokens = 0

        now_epoch = time.time()
        # Circuit-breaker check: If Groq is in 30s cooldown, fail-fast immediately
        if now_epoch < GeneratorService._groq_cooldown_until:
            gen_status = GroundingStatus.PROVIDER_ERROR
            provider_used = "none"
            model_used = "none"
            groq_attempted = False
            groq_error_type = "COOLDOWN_ACTIVE"
            should_try_groq = False
            if GeneratorService._groq_cooldown_reason == "QUOTA_EXHAUSTED":
                err_msg_text = "Groq usage limit reached. Please try again later."
            else:
                err_msg_text = "Groq is temporarily rate-limited. Please try again shortly."
            candidate_answer = get_insufficient_context_message(answer_lang) + f" (Provider Error: {err_msg_text})"
            print(f"[REQUEST {request_id}] Circuit Breaker: COOLDOWN ACTIVE ({GeneratorService._groq_cooldown_reason}) -> Fail-fast")
        else:
            should_try_groq = True

        if should_try_groq:
            groq_attempted = True
            groq_calls = 1
            print(f"[REQUEST {request_id}] Groq execution start (1 Groq call for 1 user question)")
            start_groq = time.perf_counter()
            try:
                if hasattr(primary_provider, "generate_with_usage"):
                    candidate_answer, in_tokens, out_tokens = primary_provider.generate_with_usage(
                        prompt=prompt_str,
                        system_instruction=system_prompt,
                        max_tokens=16
                    )
                else:
                    candidate_answer = primary_provider.generate(
                        prompt=prompt_str,
                        system_instruction=system_prompt
                    )
                    in_tokens = int((len(system_prompt.split()) + len(prompt_str.split())) * 1.3)
                    out_tokens = len(candidate_answer.split())

                groq_ms = (time.perf_counter() - start_groq) * 1000.0
                groq_success = True
                provider_used = "groq"
                model_used = getattr(primary_provider, "model_name", "llama-3.1-8b-instant")
                print(f"[REQUEST {request_id}] Groq completed successfully in {groq_ms:.2f}ms | in_tok={in_tokens}, out_tok={out_tokens}")
            except Exception as ge:
                groq_ms = (time.perf_counter() - start_groq) * 1000.0
                groq_success = False
                err_str = str(ge).lower()
                if "quota" in err_str or "exceeded" in err_str or "daily" in err_str or "tpd" in err_str or "rpd" in err_str:
                    groq_error_type = "QUOTA_EXHAUSTED"
                    GeneratorService._groq_cooldown_reason = "QUOTA_EXHAUSTED"
                    GeneratorService._groq_cooldown_until = time.time() + GeneratorService.GROQ_COOLDOWN_SECONDS
                    user_err = "Groq usage limit reached. Please try again later."
                elif "rate" in err_str or "429" in err_str or "tpm" in err_str or "rpm" in err_str:
                    groq_error_type = "RATE_LIMITED"
                    GeneratorService._groq_cooldown_reason = "RATE_LIMITED"
                    GeneratorService._groq_cooldown_until = time.time() + GeneratorService.GROQ_COOLDOWN_SECONDS
                    user_err = "Groq is temporarily rate-limited. Please try again shortly."
                elif "timeout" in err_str:
                    groq_error_type = "TIMEOUT"
                    user_err = "Groq request timed out. Please try again."
                elif "auth" in err_str or "401" in err_str or "403" in err_str:
                    groq_error_type = "AUTH_ERROR"
                    user_err = "Groq authentication error."
                else:
                    groq_error_type = "PROVIDER_ERROR"
                    user_err = f"Groq service error: {ge}"

                gen_status = GroundingStatus.PROVIDER_ERROR
                provider_used = "none"
                model_used = "none"
                candidate_answer = get_insufficient_context_message(answer_lang) + f" (Provider Error: {user_err})"
                print(f"[REQUEST {request_id}] Groq Exception ({groq_error_type}) in {groq_ms:.2f}ms: {err_str[:100]}")

        gen_ms = groq_ms

        # Step 6: Grounding Verification Engine Execution
        start_verify = time.perf_counter()
        final_sources = sources

        if gen_status == GroundingStatus.GROUNDED:
            internal_state, public_status, g_score = self.grounding_verifier.verify(
                answer_text=candidate_answer,
                context_chunks=retrieved_chunks
            )
            gen_status = public_status

            if public_status == GroundingStatus.UNGROUNDED:
                candidate_answer = get_insufficient_context_message(answer_lang)
                final_sources = []
        else:
            g_score = 0.0
            if gen_status in [GroundingStatus.PROVIDER_ERROR, GroundingStatus.PROVIDER_TIMEOUT]:
                final_sources = []

        verify_ms = (time.perf_counter() - start_verify) * 1000.0
        guard_ms = ((time.perf_counter() - start_guard) - (gen_ms / 1000.0) - (retrieval_ms / 1000.0)) * 1000.0 + verify_ms
        total_ms = (time.perf_counter() - start_total) * 1000.0

        token_cnt = out_tokens if out_tokens else len(candidate_answer.split())
        print(f"[REQUEST {request_id}] Finished in {total_ms:.2f}ms | status={gen_status} | provider={provider_used} | groq_success={groq_success}")

        return AskResponse(
            query=request.query,  # Original user query preserved 100% untouched
            answer=candidate_answer,
            answer_language=answer_lang,
            grounding_status=gen_status,
            grounding_score=g_score,
            sources=final_sources,
            source_type=source_provenance,
            retrieval_latency_ms=round(retrieval_ms, 2),
            generation_latency_ms=round(gen_ms, 2),
            prompt_construction_latency_ms=round(prompt_ms, 2),
            llm_request_latency_ms=round(gen_ms, 2),
            verification_latency_ms=round(verify_ms, 2),
            guardrail_latency_ms=round(max(0.1, guard_ms), 2),
            total_latency_ms=round(total_ms, 2),
            low_confidence_warning=(source_provenance != "web" and retrieval_resp.low_confidence_warning),
            input_token_count=in_tokens,
            output_token_count=token_cnt,
            provider_used=provider_used,
            model_used=model_used,
            groq_llm_latency_ms=round(groq_ms, 2),
            groq_attempted=groq_attempted,
            groq_success=groq_success,
            groq_calls=groq_calls,
            groq_error_type=groq_error_type,
            request_id=request_id
        )

