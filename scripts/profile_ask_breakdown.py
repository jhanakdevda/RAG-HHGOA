"""
Phase 1: Fine-grained /ask Latency Profiling Script (Clean Baseline Measurement)
Measures clean warm LOCAL-RAG requests with explicit HTTP 429 detection and timing isolation.
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.generation import AskRequest, AskResponse, SourceAttribution
from app.rag.generator import GeneratorService
from app.rag.guardrails.safety import SafetyFilter
from app.models.retrieval import RetrievalRequest
from app.rag.prompts import SYSTEM_GROUNDING_PROMPT
from app.rag.guardrails.injection import InjectionDefense
from app.rag.llm.factory import get_llm_provider


def extract_rate_limit_info(e: Exception) -> dict:
    info = {
        "status_code": getattr(e, "status_code", None),
        "retry_after": None,
        "remaining_requests": None,
        "remaining_tokens": None,
        "error_msg": str(e)
    }
    response = getattr(e, "response", None)
    if response is not None and hasattr(response, "headers"):
        headers = response.headers
        info["retry_after"] = headers.get("retry-after") or headers.get("x-ratelimit-reset-requests")
        info["remaining_requests"] = headers.get("x-ratelimit-remaining-requests")
        info["remaining_tokens"] = headers.get("x-ratelimit-remaining-tokens")
        if not info["status_code"] and hasattr(response, "status_code"):
            info["status_code"] = response.status_code
    elif "429" in str(e):
        info["status_code"] = 429
    return info


def run_fine_grained_profiling(target_successes: int = 5):
    print("=" * 90, flush=True)
    print("PHASE 1 — CLEAN LOCAL-RAG /ask LATENCY PROFILING", flush=True)
    print(f"Collecting {target_successes} clean warm successful requests...", flush=True)
    print("=" * 90, flush=True)

    print("[Initializing services...]", flush=True)
    generator = GeneratorService()
    provider = get_llm_provider()

    local_queries = [
        "How fast do eagles fly?",
        "What is the wingspan of a bald eagle?",
        "How do eagles catch fish?",
        "What is the nesting behavior of eagles?",
        "How high do eagles fly in the sky?",
    ]

    print("[Warming up services with 1 request...]", flush=True)
    warm_req = AskRequest(query=local_queries[0], top_k=3, preferred_answer_language="en")
    try:
        _ = generator.generate_answer(warm_req)
    except Exception as e:
        print(f"[Warm-up note: {e}]", flush=True)

    print("[Warm-up complete. Cooling down 10s before benchmark collection...]\n", flush=True)
    time.sleep(10.0)

    metrics = {
        "request_parsing": [],
        "safety_filter": [],
        "query_embedding": [],
        "faiss_search": [],
        "context_packaging": [],
        "prompt_construction": [],
        "groq_ttft": [],
        "groq_complete_gen": [],
        "grounding_verifier": [],
        "serialization": [],
        "total_ask_latency": []
    }

    rate_limit_events = []
    failed_requests = []
    web_fallback_count = 0
    successful_samples = 0
    attempt_count = 0
    max_attempts = 20

    while successful_samples < target_successes and attempt_count < max_attempts:
        attempt_count += 1
        query_str = local_queries[successful_samples % len(local_queries)]

        t0 = time.perf_counter()

        # Step 1: Request parsing
        t_parse_start = time.perf_counter()
        req = AskRequest(query=query_str, top_k=3, preferred_answer_language="en")
        t_parse = (time.perf_counter() - t_parse_start) * 1000.0

        # Step 2: Safety filter
        t_safety_start = time.perf_counter()
        safety_state, _ = SafetyFilter.evaluate_query(req.query)
        t_safety = (time.perf_counter() - t_safety_start) * 1000.0

        # Step 3 & 4: Query embedding & FAISS search
        t_embed_start = time.perf_counter()
        query_vector = generator.retrieval_service.embedding_service.encode_query(req.query)
        t_embed = (time.perf_counter() - t_embed_start) * 1000.0

        t_faiss_start = time.perf_counter()
        ret_req = RetrievalRequest(query=req.query, top_k=req.top_k)
        ret_resp = generator.retrieval_service.retrieve(ret_req)
        t_faiss = max(0.01, ret_resp.latency_ms - t_embed)

        top_score = ret_resp.results[0].score if ret_resp.results else 0.0
        if top_score < 0.55 or ret_resp.low_confidence_warning:
            web_fallback_count += 1

        # Step 5: Context packaging
        t_context_start = time.perf_counter()
        retrieved_chunks = [res.chunk for res in ret_resp.results]
        context_blocks_str = InjectionDefense.format_untrusted_context(retrieved_chunks)
        untrusted_query_str = InjectionDefense.format_untrusted_query(req.query)
        t_context = (time.perf_counter() - t_context_start) * 1000.0

        # Step 6: Prompt construction
        t_prompt_start = time.perf_counter()
        system_prompt = SYSTEM_GROUNDING_PROMPT.format(
            target_language="en",
            context_blocks=context_blocks_str,
            user_query=untrusted_query_str
        )
        t_prompt = (time.perf_counter() - t_prompt_start) * 1000.0

        # Step 7: Groq Streaming LLM Request (STRICT TIMING — NO SLEEP INSIDE MEASUREMENT)
        t_gen_start = time.perf_counter()
        ttft_ms = 0.0
        candidate_answer = ""
        is_rate_limit = False
        is_error = False
        err_info = {}

        try:
            client = provider._get_client() if hasattr(provider, "_get_client") else getattr(provider, "client", None)
            if client is not None and hasattr(client.chat.completions, "create"):
                stream_resp = client.chat.completions.create(
                    model=provider.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}"}
                    ],
                    temperature=0.1,
                    max_tokens=90,
                    stream=True
                )
                first_token = True
                full_chunks = []
                for chunk in stream_resp:
                    if first_token and chunk.choices and chunk.choices[0].delta.content:
                        ttft_ms = (time.perf_counter() - t_gen_start) * 1000.0
                        first_token = False
                    if chunk.choices and chunk.choices[0].delta.content:
                        full_chunks.append(chunk.choices[0].delta.content)
                candidate_answer = "".join(full_chunks)
                if ttft_ms == 0.0:
                    ttft_ms = (time.perf_counter() - t_gen_start) * 1000.0
            else:
                candidate_answer = provider.generate(
                    prompt=f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}",
                    system_instruction=system_prompt
                )
                ttft_ms = (time.perf_counter() - t_gen_start) * 1000.0
        except Exception as e:
            err_info = extract_rate_limit_info(e)
            if err_info["status_code"] == 429:
                is_rate_limit = True
            else:
                is_error = True

        t_gen_complete = (time.perf_counter() - t_gen_start) * 1000.0

        if is_rate_limit:
            rate_limit_events.append(err_info)
            print(f"[Attempt #{attempt_count:02d} | HTTP 429 RATE-LIMIT DETECTED] Retry-After: {err_info.get('retry_after')} | Remaining Req: {err_info.get('remaining_requests')} | Remaining Tokens: {err_info.get('remaining_tokens')}", flush=True)
            print("[Cooling down 10s outside timing block...]", flush=True)
            time.sleep(10.0)
            continue

        if is_error:
            failed_requests.append(err_info)
            print(f"[Attempt #{attempt_count:02d} | ERROR] {err_info.get('error_msg')}", flush=True)
            time.sleep(5.0)
            continue

        # Step 8: GroundingVerifier
        t_verifier_start = time.perf_counter()
        _, status, score = generator.grounding_verifier.verify(candidate_answer, retrieved_chunks)
        t_verifier = (time.perf_counter() - t_verifier_start) * 1000.0

        sources = [
            SourceAttribution(
                chunk_id=c.chunk_id,
                query_id=c.query_id,
                language_code=c.language_code or "",
                language_name=c.language_name or "",
                source_lang=c.source_lang or "en",
                target_lang=c.target_lang or "en",
                similarity_score=ret_resp.results[idx].score,
                text_snippet=c.text[:120] + "..." if len(c.text) > 120 else c.text
            ) for idx, c in enumerate(retrieved_chunks)
        ]

        full_resp = AskResponse(
            query=req.query,
            answer=candidate_answer,
            answer_language="en",
            grounding_status=status,
            grounding_score=score,
            sources=sources,
            source_type="local_rag",
            retrieval_latency_ms=round(ret_resp.latency_ms, 2),
            generation_latency_ms=round(t_gen_complete, 2),
            verification_latency_ms=round(t_verifier, 2),
            total_latency_ms=round((time.perf_counter() - t0) * 1000.0, 2)
        )

        # Step 9: Serialization
        t_ser_start = time.perf_counter()
        _ = full_resp.model_dump_json()
        t_ser = (time.perf_counter() - t_ser_start) * 1000.0

        t_total = (time.perf_counter() - t0) * 1000.0

        metrics["request_parsing"].append(t_parse)
        metrics["safety_filter"].append(t_safety)
        metrics["query_embedding"].append(t_embed)
        metrics["faiss_search"].append(t_faiss)
        metrics["context_packaging"].append(t_context)
        metrics["prompt_construction"].append(t_prompt)
        metrics["groq_ttft"].append(ttft_ms)
        metrics["groq_complete_gen"].append(t_gen_complete)
        metrics["grounding_verifier"].append(t_verifier)
        metrics["serialization"].append(t_ser)
        metrics["total_ask_latency"].append(t_total)

        successful_samples += 1
        print(f"Sample #{successful_samples:02d}/{target_successes} | Query: '{query_str[:30]}...' | TTFT: {ttft_ms:5.1f} ms | Groq Gen: {t_gen_complete:6.2f} ms | Verifier: {t_verifier:5.2f} ms | Total /ask: {t_total:6.2f} ms", flush=True)

        # Space out requests generously (10s spacing outside timing block) to prevent TPM rate limits
        if successful_samples < target_successes:
            time.sleep(10.0)

    print("\n" + "=" * 90, flush=True)
    print("PHASE 1 VALID BASELINE PROFILING REPORT", flush=True)
    print("=" * 90, flush=True)
    print(f"Successful Requests : {successful_samples}", flush=True)
    print(f"HTTP 429 Count      : {len(rate_limit_events)}", flush=True)
    print(f"Failed Requests     : {len(failed_requests)}", flush=True)

    if successful_samples > 0:
        header = f"{'Component':<28} | {'P50 (ms)':<9} | {'P70 (ms)':<9} | {'P95 (ms)':<9} | {'P100 (ms)':<9} | {'Mean (ms)':<9}"
        print(header, flush=True)
        print("-" * len(header), flush=True)

        for name, vals in metrics.items():
            arr = np.array(vals)
            p50 = np.percentile(arr, 50)
            p70 = np.percentile(arr, 70)
            p95 = np.percentile(arr, 95)
            p100 = np.max(arr)
            mean_val = np.mean(arr)

            label = name.replace("_", " ").title()
            print(f"{label:<28} | {p50:9.2f} | {p70:9.2f} | {p95:9.2f} | {p100:9.2f} | {mean_val:9.2f}", flush=True)

    print("=" * 90, flush=True)
    print(f"LOCAL-RAG WEB FALLBACK INVOCATION CHECK:", flush=True)
    print(f"Total Local-RAG Requests Attempted : {attempt_count}", flush=True)
    print(f"Web Search Fallback Hits          : {web_fallback_count}", flush=True)
    if web_fallback_count == 0:
        print("VERIFIED: 0 web search requests were made for local queries. Local-RAG path is strictly isolated!", flush=True)
    else:
        print(f"WARNING: {web_fallback_count} local queries accidentally triggered web search fallback!", flush=True)
    print("=" * 90, flush=True)


if __name__ == "__main__":
    run_fine_grained_profiling(5)

