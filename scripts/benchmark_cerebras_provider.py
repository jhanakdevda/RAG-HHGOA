"""
Benchmark Cerebras LLM Provider
Measures TTFT, Complete Generation Latency, GroundingVerifier latency, and Total /ask latency
over 10 warm successful requests across English, Hindi, Marathi, and Bengali queries.
Compares directly against Groq llama-3.1-8b-instant production baseline.
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

from app.models.generation import AskRequest
from app.models.retrieval import RetrievalRequest
from app.rag.generator import GeneratorService
from app.rag.guardrails.safety import SafetyFilter
from app.rag.guardrails.injection import InjectionDefense
from app.rag.prompts import SYSTEM_GROUNDING_PROMPT
from app.rag.llm.factory import get_llm_provider


def benchmark_cerebras_model(model_name: str, target_successes: int = 10) -> Dict[str, Any]:
    print("\n" + "=" * 95, flush=True)
    print(f"BENCHMARKING CEREBRAS MODEL: {model_name}", flush=True)
    print("=" * 95, flush=True)

    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        print("  Error: CEREBRAS_API_KEY is missing.", flush=True)
        return {"model": model_name, "status": "UNAVAILABLE", "error": "CEREBRAS_API_KEY missing"}

    try:
        provider = get_llm_provider(
            provider_name="cerebras",
            model_name=model_name,
            api_key=key,
            base_url="https://api.cerebras.ai/v1"
        )
        generator = GeneratorService(llm_provider=provider)
    except Exception as e:
        print(f"  Provider initialization error: {e}", flush=True)
        return {"model": model_name, "status": "UNAVAILABLE", "error": str(e)}

    test_queries = [
        {"query": "How fast do eagles fly?", "lang": "en", "kw": "30"},
        {"query": "What is the wingspan of a bald eagle?", "lang": "en", "kw": "feet"},
        {"query": "How do eagles catch fish?", "lang": "en", "kw": "water"},
        {"query": "What is the nesting behavior of eagles?", "lang": "en", "kw": "nest"},
        {"query": "चील कितनी तेजी से उड़ती है?", "lang": "hi", "kw": "30"},
        {"query": "गरुड किती वेगाने उडतो?", "lang": "mr", "kw": "30"},
        {"query": "ইগল কত দ্রুত উড়ে?", "lang": "bn", "kw": "30"}
    ]

    print("[Warming up Cerebras service with 1 request...]", flush=True)
    try:
        _ = generator.generate_answer(AskRequest(query=test_queries[0]["query"], top_k=3))
    except Exception as e:
        print(f"  Warmup error: {e}", flush=True)

    print("[Warmup complete. Inter-request spacing 5s...]\n", flush=True)
    time.sleep(5.0)

    ttft_list = []
    complete_gen_list = []
    verifier_list = []
    total_ask_list = []
    grounding_scores = []
    grounding_statuses = []
    sample_answers = []

    rate_limit_count = 0
    failure_count = 0
    successful_count = 0
    attempt = 0
    max_attempts = 20

    while successful_count < target_successes and attempt < max_attempts:
        attempt += 1
        q_item = test_queries[successful_count % len(test_queries)]
        q_text = q_item["query"]
        q_lang = q_item["lang"]

        t0 = time.perf_counter()

        # Step 1: Safety screening
        safety_state, _ = SafetyFilter.evaluate_query(q_text)

        # Step 2: Retrieval
        ret_req = RetrievalRequest(query=q_text, top_k=3)
        ret_resp = generator.retrieval_service.retrieve(ret_req)
        retrieved_chunks = [r.chunk for r in ret_resp.results]

        # Step 3: Context & prompt packaging
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
            if client is None:
                import openai
                client = openai.OpenAI(api_key=key, base_url="https://api.cerebras.ai/v1", timeout=15.0)

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
        except Exception as e:
            if "429" in str(e):
                is_429 = True
                rate_limit_count += 1
            else:
                failure_count += 1
                print(f"  Attempt #{attempt:02d} error: {e}", flush=True)

        t_gen_complete = (time.perf_counter() - t_gen_start) * 1000.0

        if is_429:
            print(f"  [Attempt #{attempt:02d} | 429 Rate Limit] Cooling down 8s...", flush=True)
            time.sleep(8.0)
            continue

        if not candidate_answer:
            time.sleep(3.0)
            continue

        # Step 5: GroundingVerifier
        t_ver_start = time.perf_counter()
        _, status, score = generator.grounding_verifier.verify(candidate_answer, retrieved_chunks)
        t_ver = (time.perf_counter() - t_ver_start) * 1000.0

        t_total = (time.perf_counter() - t0) * 1000.0

        ttft_list.append(ttft_ms)
        complete_gen_list.append(t_gen_complete)
        verifier_list.append(t_ver)
        total_ask_list.append(t_total)
        grounding_scores.append(score)
        grounding_statuses.append(status.value)
        sample_answers.append(candidate_answer)

        successful_count += 1
        print(f"  Sample #{successful_count:02d}/{target_successes} | Lang: {q_lang} | TTFT: {ttft_ms:5.1f} ms | Gen: {t_gen_complete:6.2f} ms | Verifier: {t_ver:5.2f} ms | Total /ask: {t_total:6.2f} ms", flush=True)

        if successful_count < target_successes:
            time.sleep(5.0)

    if successful_count == 0:
        return {
            "model": model_name,
            "success_count": 0,
            "failure_count": failure_count,
            "rate_limit_count": rate_limit_count,
            "status": "FAILED"
        }

    ttft_arr = np.array(ttft_list)
    gen_arr = np.array(complete_gen_list)
    ver_arr = np.array(verifier_list)
    tot_arr = np.array(total_ask_list)

    return {
        "model": model_name,
        "success_count": successful_count,
        "failure_count": failure_count,
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
        "total_ask_p95": float(np.percentile(tot_arr, 95)),
        "total_ask_p100": float(np.max(tot_arr)),
        "avg_grounding_score": float(np.mean(grounding_scores)),
        "status": grounding_statuses[0] if grounding_statuses else "N/A",
        "sample_answers": sample_answers[:2]
    }


def run_cerebras_benchmark_suite():
    print("=" * 95, flush=True)
    print("CEREBRAS PROVIDER BENCHMARK VS GROQ BASELINE", flush=True)
    print("=" * 95, flush=True)

    cerebras_models = ["gemma-4-31b", "gpt-oss-120b", "zai-glm-4.7"]
    results = []

    for m in cerebras_models:
        res = benchmark_cerebras_model(m, target_successes=10)
        results.append(res)
        time.sleep(5.0)

    print("\n" + "=" * 115, flush=True)
    print("CEREBRAS VS GROQ COMPARATIVE BENCHMARK TABLE", flush=True)
    print("=" * 115, flush=True)
    header = f"{'Provider':<10} | {'Model':<18} | {'Succ/Fail/429':<13} | {'TTFT P50':<9} | {'Gen P50':<9} | {'Ver P50':<8} | {'Total P50':<9} | {'Total P70':<9} | {'Total P100':<10} | {'G-Score':<7}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    # Groq Production Baseline
    print(f"{'groq':<10} | {'llama-3.1-8b-inst':<18} | {'10/0/0':<13} | {'282.5ms':<9} | {'337.4ms':<9} | {'56.5ms':<8} | {'464.7ms':<9} | {'485.5ms':<9} | {'643.99ms':<10} | {'0.4345':<7}", flush=True)

    for r in results:
        mdl = r["model"][:18]
        if r.get("success_count", 0) == 0:
            s_str = f"{r.get('success_count',0)}/{r.get('failure_count',0)}/{r.get('rate_limit_count',0)}"
            print(f"{'cerebras':<10} | {mdl:<18} | {s_str:<13} | {'N/A':<9} | {'N/A':<9} | {'N/A':<8} | {'N/A':<9} | {'N/A':<9} | {'N/A':<10} | {'N/A':<7}", flush=True)
        else:
            s_str = f"{r['success_count']}/{r['failure_count']}/{r['rate_limit_count']}"
            ttft = f"{r['ttft_p50']:6.1f}ms"
            gen = f"{r['gen_p50']:6.1f}ms"
            ver = f"{r['verifier_p50']:5.1f}ms"
            tot50 = f"{r['total_ask_p50']:6.1f}ms"
            tot70 = f"{r['total_ask_p70']:6.1f}ms"
            tot100 = f"{r['total_ask_p100']:7.1f}ms"
            g_sc = f"{r['avg_grounding_score']:6.4f}"
            print(f"{'cerebras':<10} | {mdl:<18} | {s_str:<13} | {ttft:<9} | {gen:<9} | {ver:<8} | {tot50:<9} | {tot70:<9} | {tot100:<10} | {g_sc:<7}", flush=True)

    print("=" * 115, flush=True)


if __name__ == "__main__":
    run_cerebras_benchmark_suite()
