"""
Phase 8: Controlled LLM Provider & Model Latency Benchmark Script
Systematically evaluates available LLM models on Groq LPUs and OpenAI-compatible adapters
under identical prompt, context, top_k=3, max_tokens=48, and guardrail parameters.
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
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


def benchmark_model_candidate(provider_name: str, model_name: str, base_url: str = None, target_successes: int = 10) -> Dict[str, Any]:
    print("\n" + "=" * 90, flush=True)
    print(f"BENCHMARKING MODEL: Provider={provider_name} | Model={model_name}", flush=True)
    print("=" * 90, flush=True)

    settings = get_settings()
    try:
        provider = get_llm_provider(provider_name=provider_name, model_name=model_name, base_url=base_url)
        generator = GeneratorService(llm_provider=provider)
    except Exception as e:
        print(f"Provider initialization failed for {provider_name}/{model_name}: {e}", flush=True)
        return {
            "provider": provider_name,
            "model": model_name,
            "success_count": 0,
            "rate_limit_count": 0,
            "status": "UNAVAILABLE",
            "error": str(e)
        }

    test_queries = [
        {"query": "How fast do eagles fly?", "lang": "en", "kw": "30"},
        {"query": "What is the wingspan of a bald eagle?", "lang": "en", "kw": "feet"},
        {"query": "How do eagles catch fish?", "lang": "en", "kw": "water"},
        {"query": "What is the nesting behavior of eagles?", "lang": "en", "kw": "nest"},
        {"query": "चील कितनी तेजी से उड़ती है?", "lang": "hi", "kw": "30"},
        {"query": "गरुड किती वेगाने उडतो?", "lang": "mr", "kw": "३०"},
        {"query": "ইগল কত দ্রুত উড়ে?", "lang": "bn", "kw": "৩০"}
    ]

    print("[Warming up service with 1 request...]", flush=True)
    try:
        _ = generator.generate_answer(AskRequest(query=test_queries[0]["query"], top_k=3))
    except Exception as e:
        print(f"  Warmup error: {e}", flush=True)

    print("[Warmup complete. Spacing requests by 8s outside measurement blocks...]\n", flush=True)
    time.sleep(8.0)

    ttft_list = []
    complete_gen_list = []
    verifier_list = []
    total_ask_list = []
    output_tokens_list = []
    grounding_scores = []
    grounding_statuses = []
    sample_answers = []

    rate_limit_count = 0
    successful_count = 0
    attempt = 0
    max_attempts = 25

    while successful_count < target_successes and attempt < max_attempts:
        attempt += 1
        q_item = test_queries[successful_count % len(test_queries)]
        q_text = q_item["query"]
        q_lang = q_item["lang"]

        t0 = time.perf_counter()

        # Step 1: Safety screening
        safety_state, _ = SafetyFilter.evaluate_query(q_text)

        # Step 2: Dense retrieval with top_k=3
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

        # Step 4: Measured LLM Generation
        t_gen_start = time.perf_counter()
        ttft_ms = 0.0
        candidate_answer = ""
        is_429 = False

        try:
            client = provider._get_client() if hasattr(provider, "_get_client") else None
            if client is not None:
                stream_resp = client.chat.completions.create(
                    model=model_name,
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
            else:
                candidate_answer = provider.generate(
                    prompt=f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}",
                    system_instruction=system_prompt
                )
                ttft_ms = (time.perf_counter() - t_gen_start) * 1000.0
        except Exception as e:
            err_info = extract_rate_limit_info(e)
            if err_info["status_code"] == 429:
                is_429 = True
                rate_limit_count += 1
            else:
                print(f"  Attempt #{attempt:02d} error: {e}", flush=True)

        t_gen_complete = (time.perf_counter() - t_gen_start) * 1000.0

        if is_429:
            print(f"  [Attempt #{attempt:02d} | HTTP 429] Cooling down 9s outside timing...", flush=True)
            time.sleep(9.0)
            continue

        if not candidate_answer:
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
        output_tokens_list.append(tok_cnt)
        grounding_scores.append(score)
        grounding_statuses.append(status.value)
        sample_answers.append(candidate_answer)

        successful_count += 1
        print(f"  Sample #{successful_count:02d}/{target_successes} | Lang: {q_lang} | TTFT: {ttft_ms:5.1f} ms | Gen: {t_gen_complete:6.2f} ms | Verifier: {t_ver:5.2f} ms | Total /ask: {t_total:6.2f} ms", flush=True)

        if successful_count < target_successes:
            time.sleep(8.0)

    if successful_count == 0:
        return {
            "provider": provider_name,
            "model": model_name,
            "success_count": 0,
            "rate_limit_count": rate_limit_count,
            "status": "FAILED"
        }

    ttft_arr = np.array(ttft_list)
    gen_arr = np.array(complete_gen_list)
    ver_arr = np.array(verifier_list)
    tot_arr = np.array(total_ask_list)

    return {
        "provider": provider_name,
        "model": model_name,
        "success_count": successful_count,
        "rate_limit_count": rate_limit_count,
        "ttft_p50": float(np.percentile(ttft_arr, 50)),
        "ttft_p70": float(np.percentile(ttft_arr, 70)),
        "ttft_p95": float(np.percentile(ttft_arr, 95)),
        "ttft_p100": float(np.max(ttft_arr)),
        "gen_p50": float(np.percentile(gen_arr, 50)),
        "gen_p70": float(np.percentile(gen_arr, 70)),
        "gen_p95": float(np.percentile(gen_arr, 95)),
        "gen_p100": float(np.max(gen_arr)),
        "verifier_p50": float(np.percentile(ver_arr, 50)),
        "total_ask_p50": float(np.percentile(tot_arr, 50)),
        "total_ask_p70": float(np.percentile(tot_arr, 70)),
        "total_ask_p100": float(np.max(tot_arr)),
        "tokens_p50": int(np.percentile(output_tokens_list, 50)),
        "avg_grounding_score": float(np.mean(grounding_scores)),
        "status": grounding_statuses[0] if grounding_statuses else "N/A",
        "sample_answers": sample_answers[:2]
    }


def run_phase8_controlled_benchmark():
    print("=" * 90, flush=True)
    print("PHASE 8: CONTROLLED LLM PROVIDER & MODEL LATENCY BENCHMARK", flush=True)
    print("=" * 90, flush=True)

    candidates = [
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "groq", "model": "llama-3.1-8b-instant"},
        {"provider": "groq", "model": "mixtral-8x7b-32768"},
        {"provider": "groq", "model": "gemma2-9b-it"},
        {"provider": "cerebras", "model": "llama3.1-8b", "base_url": "https://api.cerebras.ai/v1"},
        {"provider": "fireworks", "model": "accounts/fireworks/models/llama-v3p1-8b-instruct", "base_url": "https://api.fireworks.ai/inference/v1"},
        {"provider": "sambanova", "model": "Meta-Llama-3.1-8B-Instruct", "base_url": "https://api.sambanova.ai/v1"},
        {"provider": "together", "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "base_url": "https://api.together.xyz/v1"}
    ]

    results = []
    for cand in candidates:
        res = benchmark_model_candidate(
            provider_name=cand["provider"],
            model_name=cand["model"],
            base_url=cand.get("base_url"),
            target_successes=10
        )
        results.append(res)
        time.sleep(8.0)

    print("\n" + "=" * 110, flush=True)
    print("PHASE 8 COMPARATIVE LLM BENCHMARK REPORT TABLE", flush=True)
    print("=" * 110, flush=True)
    header = f"{'Provider':<10} | {'Model':<24} | {'Succ/429':<8} | {'TTFT P50':<9} | {'Gen P50':<9} | {'Ver P50':<8} | {'Total P50':<9} | {'Total P100':<10} | {'G-Score':<7} | {'Status':<18}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    for r in results:
        prov = r["provider"]
        mdl = r["model"][:24]
        if r.get("success_count", 0) == 0:
            succ = f"{r.get('success_count',0)}/{r.get('rate_limit_count',0)}"
            print(f"{prov:<10} | {mdl:<24} | {succ:<8} | {'N/A':<9} | {'N/A':<9} | {'N/A':<8} | {'N/A':<9} | {'N/A':<10} | {'N/A':<7} | {r.get('status', 'UNAVAILABLE'):<18}", flush=True)
        else:
            succ = f"{r['success_count']}/{r['rate_limit_count']}"
            ttft = f"{r['ttft_p50']:6.1f}ms"
            gen = f"{r['gen_p50']:6.1f}ms"
            ver = f"{r['verifier_p50']:5.1f}ms"
            tot50 = f"{r['total_ask_p50']:6.1f}ms"
            tot100 = f"{r['total_ask_p100']:7.1f}ms"
            g_sc = f"{r['avg_grounding_score']:6.4f}"
            stat = r["status"]
            print(f"{prov:<10} | {mdl:<24} | {succ:<8} | {ttft:<9} | {gen:<9} | {ver:<8} | {tot50:<9} | {tot100:<10} | {g_sc:<7} | {stat:<18}", flush=True)

    print("=" * 110, flush=True)


if __name__ == "__main__":
    run_phase8_controlled_benchmark()
