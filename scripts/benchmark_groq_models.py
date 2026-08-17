"""
Phase 4: Groq Candidate Models Latency & Quality Benchmark Script
Evaluates candidate models on Groq API using the existing provider abstraction.
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import get_settings
from app.models.generation import AskRequest, AskResponse
from app.models.retrieval import RetrievalRequest
from app.rag.generator import GeneratorService
from app.rag.guardrails.safety import SafetyFilter
from app.rag.guardrails.injection import InjectionDefense
from app.rag.prompts import SYSTEM_GROUNDING_PROMPT
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


def benchmark_candidate_model(model_name: str, target_successes: int = 3) -> Dict[str, Any]:
    print("-" * 90, flush=True)
    print(f"BENCHMARKING CANDIDATE MODEL: {model_name}", flush=True)
    print("-" * 90, flush=True)

    settings = get_settings()
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")

    try:
        provider = get_llm_provider(provider_name="groq", model_name=model_name, api_key=api_key)
        generator = GeneratorService(llm_provider=provider)
    except Exception as e:
        print(f"FAILED to initialize provider for model '{model_name}': {e}", flush=True)
        return {"model": model_name, "error": str(e), "success_count": 0}

    test_queries = [
        {"query": "How fast do eagles fly?", "lang": "en"},
        {"query": "How do eagles catch fish?", "lang": "en"},
        {"query": "चील कितनी तेजी से उड़ती है?", "lang": "hi"}
    ]

    ttft_list = []
    complete_gen_list = []
    total_ask_list = []
    verifier_list = []
    output_tokens_list = []
    grounding_statuses = []
    answers = []
    rate_limit_count = 0
    error_count = 0
    successful_count = 0
    attempt = 0
    max_attempts = 12

    while successful_count < target_successes and attempt < max_attempts:
        attempt += 1
        q_item = test_queries[successful_count % len(test_queries)]
        q_text = q_item["query"]
        q_lang = q_item["lang"]

        t0 = time.perf_counter()

        # Step 1: Safety screening
        safety_state, _ = SafetyFilter.evaluate_query(q_text)

        # Step 2: Dense retrieval
        ret_req = RetrievalRequest(query=q_text, top_k=3)
        ret_resp = generator.retrieval_service.retrieve(ret_req)
        retrieved_chunks = [r.chunk for r in ret_resp.results]

        # Step 3: Context & prompt formatting
        context_blocks_str = InjectionDefense.format_untrusted_context(retrieved_chunks)
        untrusted_query_str = InjectionDefense.format_untrusted_query(q_text)
        system_prompt = SYSTEM_GROUNDING_PROMPT.format(
            target_language=q_lang,
            context_blocks=context_blocks_str,
            user_query=untrusted_query_str
        )

        # Step 4: Measured LLM Execution
        t_gen_start = time.perf_counter()
        ttft_ms = 0.0
        candidate_answer = ""
        is_429 = False
        is_err = False

        try:
            client = provider._get_client()
            stream_resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}"}
                ],
                temperature=0.1,
                max_tokens=90,
                stream=True
            )
            first_token = True
            chunks = []
            for chunk in stream_resp:
                if first_token and chunk.choices and chunk.choices[0].delta.content:
                    ttft_ms = (time.perf_counter() - t_gen_start) * 1000.0
                    first_token = False
                if chunk.choices and chunk.choices[0].delta.content:
                    chunks.append(chunk.choices[0].delta.content)
            candidate_answer = "".join(chunks)
            if ttft_ms == 0.0:
                ttft_ms = (time.perf_counter() - t_gen_start) * 1000.0
        except Exception as e:
            err_info = extract_rate_limit_info(e)
            if err_info["status_code"] == 429:
                is_429 = True
                rate_limit_count += 1
            else:
                is_err = True
                error_count += 1
                print(f"  [Attempt #{attempt}] Error with '{model_name}': {e}", flush=True)

        t_gen_complete = (time.perf_counter() - t_gen_start) * 1000.0

        if is_429:
            print(f"  [Attempt #{attempt}] HTTP 429 Rate Limit for '{model_name}'. Cooling down 8s outside timing...", flush=True)
            time.sleep(8.0)
            continue

        if is_err:
            time.sleep(4.0)
            continue

        # Step 5: Grounding Verification
        t_ver_start = time.perf_counter()
        _, status, score = generator.grounding_verifier.verify(candidate_answer, retrieved_chunks)
        t_ver = (time.perf_counter() - t_ver_start) * 1000.0

        t_total = (time.perf_counter() - t0) * 1000.0
        token_cnt = len(candidate_answer.split())

        ttft_list.append(ttft_ms)
        complete_gen_list.append(t_gen_complete)
        total_ask_list.append(t_total)
        verifier_list.append(t_ver)
        output_tokens_list.append(token_cnt)
        grounding_statuses.append(status.value)
        answers.append(candidate_answer)

        successful_count += 1
        print(f"  Sample #{successful_count}/{target_successes} | Lang: {q_lang} | TTFT: {ttft_ms:5.1f} ms | Gen: {t_gen_complete:6.2f} ms | Total /ask: {t_total:6.2f} ms | Tokens: {token_cnt}", flush=True)
        print(f"  Answer: '{candidate_answer[:80]}...'\n", flush=True)

        if successful_count < target_successes:
            time.sleep(8.0)

    if successful_count == 0:
        return {"model": model_name, "error": "No successful samples", "success_count": 0, "rate_limit_count": rate_limit_count}

    return {
        "model": model_name,
        "success_count": successful_count,
        "rate_limit_count": rate_limit_count,
        "ttft_p50": float(np.percentile(ttft_list, 50)),
        "ttft_p95": float(np.percentile(ttft_list, 95)),
        "gen_p50": float(np.percentile(complete_gen_list, 50)),
        "gen_p95": float(np.percentile(complete_gen_list, 95)),
        "total_ask_p50": float(np.percentile(total_ask_list, 50)),
        "total_ask_p95": float(np.percentile(total_ask_list, 95)),
        "verifier_p50": float(np.percentile(verifier_list, 50)),
        "output_tokens_p50": int(np.percentile(output_tokens_list, 50)),
        "grounding_statuses": grounding_statuses,
        "sample_answers": answers
    }


def run_groq_comparison():
    candidate_models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "gemma2-9b-it",
        "llama-3.2-1b-preview",
        "llama-3.2-3b-preview"
    ]

    print("=" * 90, flush=True)
    print("PHASE 2 / PHASE 4: GROQ CANDIDATE MODELS BENCHMARK COMPARISON", flush=True)
    print("=" * 90, flush=True)

    results = []
    for model in candidate_models:
        res = benchmark_candidate_model(model, target_successes=3)
        results.append(res)
        time.sleep(10.0)

    print("\n" + "=" * 90, flush=True)
    print("GROQ MODELS BENCHMARK COMPARISON SUMMARY TABLE", flush=True)
    print("=" * 90, flush=True)
    header = f"{'Model':<25} | {'Success':<7} | {'429s':<5} | {'TTFT P50':<9} | {'Gen P50':<9} | {'Total P50':<10} | {'Tokens':<6} | {'Status':<10}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    for r in results:
        if r.get("success_count", 0) > 0:
            m_name = r["model"]
            succ = r["success_count"]
            r429 = r["rate_limit_count"]
            ttft = f"{r['ttft_p50']:7.1f} ms"
            gen = f"{r['gen_p50']:7.1f} ms"
            tot = f"{r['total_ask_p50']:8.1f} ms"
            tok = r["output_tokens_p50"]
            stat = r["grounding_statuses"][0]
            print(f"{m_name:<25} | {succ:<7} | {r429:<5} | {ttft:<9} | {gen:<9} | {tot:<10} | {tok:<6} | {stat:<10}", flush=True)
        else:
            print(f"{r['model']:<25} | {0:<7} | {r.get('rate_limit_count',0):<5} | ERROR: {r.get('error', 'N/A')[:30]}", flush=True)

    print("=" * 90, flush=True)


if __name__ == "__main__":
    run_groq_comparison()
