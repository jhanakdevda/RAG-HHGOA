"""
Phase 6D: TTFT & Complete Latency Feasibility Benchmark Script
Executes 10 warm successful requests to evaluate realistic latency bounds under optimal configuration.
"""

import os
import sys
import time
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import get_settings
from app.models.generation import AskRequest
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


def run_feasibility_benchmark(target_successes: int = 10):
    print("=" * 90, flush=True)
    print("PHASE 6D — TTFT & COMPLETE LATENCY FEASIBILITY BENCHMARK (10 SUCCESSFUL REQUESTS)", flush=True)
    print("=" * 90, flush=True)

    settings = get_settings()
    provider = get_llm_provider(model_name="llama-3.3-70b-versatile")
    generator = GeneratorService(llm_provider=provider)

    test_queries = [
        {"query": "How fast do eagles fly?", "lang": "en"},
        {"query": "What is the wingspan of a bald eagle?", "lang": "en"},
        {"query": "How do eagles catch fish?", "lang": "en"},
        {"query": "What is the nesting behavior of eagles?", "lang": "en"},
        {"query": "चील कितनी तेजी से उड़ती है?", "lang": "hi"},
        {"query": "गरुड किती वेगाने उडतो?", "lang": "mr"}
    ]

    print("[Warming up services with 1 request...]", flush=True)
    try:
        _ = generator.generate_answer(AskRequest(query=test_queries[0]["query"], top_k=3))
    except Exception:
        pass

    print("[Warm-up complete. Cooling down 10s before benchmarking...]\n", flush=True)
    time.sleep(10.0)

    ttft_list = []
    complete_gen_list = []
    verifier_list = []
    total_ask_list = []
    token_cnt_list = []

    rate_limit_events = []
    failed_requests = []
    successful_count = 0
    attempt = 0
    max_attempts = 25

    while successful_count < target_successes and attempt < max_attempts:
        attempt += 1
        q_item = test_queries[successful_count % len(test_queries)]
        q_text = q_item["query"]
        q_lang = q_item["lang"]

        t0 = time.perf_counter()

        # Step 1: Safety filter
        safety_state, _ = SafetyFilter.evaluate_query(q_text)

        # Step 2: Vector retrieval
        ret_req = RetrievalRequest(query=q_text, top_k=3)
        ret_resp = generator.retrieval_service.retrieve(ret_req)
        retrieved_chunks = [r.chunk for r in ret_resp.results]

        # Step 3: Context & prompt construction
        context_blocks_str = InjectionDefense.format_untrusted_context(retrieved_chunks)
        untrusted_query_str = InjectionDefense.format_untrusted_query(q_text)
        system_prompt = SYSTEM_GROUNDING_PROMPT.format(
            target_language=q_lang,
            context_blocks=context_blocks_str,
            user_query=untrusted_query_str
        )

        # Step 4: Groq Streaming LLM Request (max_tokens=48)
        t_gen_start = time.perf_counter()
        ttft_ms = 0.0
        candidate_answer = ""
        is_429 = False
        is_err = False
        err_info = {}

        try:
            client = provider._get_client()
            stream_resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}"}
                ],
                temperature=0.1,
                max_tokens=48,
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
            else:
                is_err = True

        t_gen_complete = (time.perf_counter() - t_gen_start) * 1000.0

        if is_429:
            rate_limit_events.append(err_info)
            print(f"[Attempt #{attempt:02d} | HTTP 429] Retry-After: {err_info.get('retry_after')}s. Cooling down 10s outside timing...", flush=True)
            time.sleep(10.0)
            continue

        if is_err:
            failed_requests.append(err_info)
            time.sleep(5.0)
            continue

        # Step 5: GroundingVerifier
        t_ver_start = time.perf_counter()
        _, status, score = generator.grounding_verifier.verify(candidate_answer, retrieved_chunks)
        t_ver = (time.perf_counter() - t_ver_start) * 1000.0

        t_total = (time.perf_counter() - t0) * 1000.0
        tok_cnt = len(candidate_answer.split())

        ttft_list.append(ttft_ms)
        complete_gen_list.append(t_gen_complete)
        verifier_list.append(t_ver)
        total_ask_list.append(t_total)
        token_cnt_list.append(tok_cnt)

        successful_count += 1
        print(f"Sample #{successful_count:02d}/{target_successes} | Lang: {q_lang} | TTFT: {ttft_ms:5.1f} ms | Gen: {t_gen_complete:6.2f} ms | Verifier: {t_ver:5.2f} ms | Total /ask: {t_total:6.2f} ms", flush=True)

        if successful_count < target_successes:
            time.sleep(10.0)

    print("\n" + "=" * 90, flush=True)
    print("PHASE 6D FEASIBILITY BENCHMARK REPORT (10 SUCCESSFUL SAMPLES)", flush=True)
    print("=" * 90, flush=True)
    print(f"Successful Requests : {successful_count}", flush=True)
    print(f"HTTP 429 Count      : {len(rate_limit_events)}", flush=True)
    print(f"Failed Requests     : {len(failed_requests)}\n", flush=True)

    header = f"{'Metric':<30} | {'P50 (ms)':<10} | {'P70 (ms)':<10} | {'P95 (ms)':<10} | {'Mean (ms)':<10}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    metrics_map = {
        "Groq TTFT (First Token)": ttft_list,
        "Groq Complete Generation": complete_gen_list,
        "GroundingVerifier Latency": verifier_list,
        "Total End-to-End /ask Latency": total_ask_list
    }

    for label, vals in metrics_map.items():
        arr = np.array(vals)
        print(f"{label:<30} | {np.percentile(arr, 50):10.2f} | {np.percentile(arr, 70):10.2f} | {np.percentile(arr, 95):10.2f} | {np.mean(arr):10.2f}", flush=True)

    print("=" * 90, flush=True)


if __name__ == "__main__":
    run_feasibility_benchmark(10)
