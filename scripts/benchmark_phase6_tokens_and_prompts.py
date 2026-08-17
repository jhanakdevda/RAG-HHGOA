"""
Phase 6A & 6B: Token Budget and Context Window Latency Benchmark Script
Systematically evaluates max_tokens (90, 64, 48, 32) and Top-K context (Top-3 vs Top-2).
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


def benchmark_config(max_tokens_val: int, top_k_val: int, target_successes: int = 4) -> Dict[str, Any]:
    print("-" * 90, flush=True)
    print(f"BENCHMARKING CONFIG: max_tokens={max_tokens_val} | top_k={top_k_val}", flush=True)
    print("-" * 90, flush=True)

    settings = get_settings()
    provider = get_llm_provider(model_name="llama-3.3-70b-versatile")
    generator = GeneratorService(llm_provider=provider)

    test_queries = [
        {"query": "How fast do eagles fly?", "lang": "en"},
        {"query": "What is the wingspan of a bald eagle?", "lang": "en"},
        {"query": "चील कितनी तेजी से उड़ती है?", "lang": "hi"},
        {"query": "गरुड किती वेगाने उडतो?", "lang": "mr"}
    ]

    ttft_list = []
    complete_gen_list = []
    total_ask_list = []
    output_tokens_list = []
    grounding_scores = []
    grounding_statuses = []
    sample_answers = []
    rate_limit_count = 0
    successful_count = 0
    attempt = 0
    max_attempts = 15

    while successful_count < target_successes and attempt < max_attempts:
        attempt += 1
        q_item = test_queries[successful_count % len(test_queries)]
        q_text = q_item["query"]
        q_lang = q_item["lang"]

        t0 = time.perf_counter()

        # Step 1: Safety screening
        safety_state, _ = SafetyFilter.evaluate_query(q_text)

        # Step 2: Dense retrieval with top_k_val
        ret_req = RetrievalRequest(query=q_text, top_k=top_k_val)
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

        try:
            client = provider._get_client()
            stream_resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}"}
                ],
                temperature=0.1,
                max_tokens=max_tokens_val,
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

        t_gen_complete = (time.perf_counter() - t_gen_start) * 1000.0

        if is_429:
            print(f"  [Attempt #{attempt}] HTTP 429. Cooling down 8s outside timing...", flush=True)
            time.sleep(8.0)
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
        output_tokens_list.append(token_cnt)
        grounding_scores.append(score)
        grounding_statuses.append(status.value)
        sample_answers.append(candidate_answer)

        successful_count += 1
        print(f"  Sample #{successful_count}/{target_successes} | Lang: {q_lang} | TTFT: {ttft_ms:5.1f} ms | Gen: {t_gen_complete:6.2f} ms | Total /ask: {t_total:6.2f} ms | Tokens: {token_cnt}", flush=True)
        print(f"  Answer: '{candidate_answer[:80]}...'\n", flush=True)

        if successful_count < target_successes:
            time.sleep(7.0)

    return {
        "max_tokens": max_tokens_val,
        "top_k": top_k_val,
        "success_count": successful_count,
        "rate_limit_count": rate_limit_count,
        "ttft_p50": float(np.percentile(ttft_list, 50)),
        "gen_p50": float(np.percentile(complete_gen_list, 50)),
        "total_ask_p50": float(np.percentile(total_ask_list, 50)),
        "output_tokens_p50": int(np.percentile(output_tokens_list, 50)),
        "avg_grounding_score": float(np.mean(grounding_scores)),
        "status": grounding_statuses[0] if grounding_statuses else "N/A",
        "sample_answers": sample_answers
    }


def run_phase6_comparison():
    print("=" * 90, flush=True)
    print("PHASE 6A & 6B: TOKEN BUDGET & CONTEXT WINDOW LATENCY BENCHMARK", flush=True)
    print("=" * 90, flush=True)

    test_configs = [
        {"max_tokens": 90, "top_k": 3},
        {"max_tokens": 64, "top_k": 3},
        {"max_tokens": 48, "top_k": 3},
        {"max_tokens": 32, "top_k": 3},
        {"max_tokens": 48, "top_k": 2},
    ]

    results = []
    for cfg in test_configs:
        res = benchmark_config(cfg["max_tokens"], cfg["top_k"], target_successes=4)
        results.append(res)
        time.sleep(8.0)

    print("\n" + "=" * 90, flush=True)
    print("PHASE 6A & 6B BENCHMARK SUMMARY TABLE", flush=True)
    print("=" * 90, flush=True)
    header = f"{'max_tokens':<10} | {'top_k':<6} | {'TTFT P50':<9} | {'Gen P50':<9} | {'Total P50':<10} | {'Tokens':<6} | {'G-Score':<7} | {'Status':<18}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    for r in results:
        m_tok = r["max_tokens"]
        tk = r["top_k"]
        ttft = f"{r['ttft_p50']:7.1f} ms"
        gen = f"{r['gen_p50']:7.1f} ms"
        tot = f"{r['total_ask_p50']:8.1f} ms"
        tok = r["output_tokens_p50"]
        g_sc = f"{r['avg_grounding_score']:6.4f}"
        stat = r["status"]
        print(f"{m_tok:<10} | {tk:<6} | {ttft:<9} | {gen:<9} | {tot:<10} | {tok:<6} | {g_sc:<7} | {stat:<18}", flush=True)

    print("=" * 90, flush=True)


if __name__ == "__main__":
    run_phase6_comparison()
