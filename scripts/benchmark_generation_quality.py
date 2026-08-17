"""
Phase 9 Optimization — End-to-End RAG Answer & Grounding Quality Benchmark

Evaluates GeneratorService across 1,400 ground-truth records (21,573 FAISS vectors):
- Grounded, Partially Grounded, Ungrounded rates
- Measured latency breakdowns (retrieval, generation, guardrail, total)
- Grounding score distribution
"""

import os
import sys
import json
import time
import numpy as np
from typing import List, Dict

# Force UTF-8 stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.dataset import MSMarcoExample
from app.models.generation import AskRequest, GroundingStatus
from app.rag.generator import GeneratorService

SAMPLE_PATH = os.path.join("data", "sample", "msmarco_xi_expanded_sample.jsonl")


def run_generation_quality_benchmark():
    print("=" * 95)
    print("Real LLM Generation & Quality Baseline Benchmark")
    print("=" * 95)

    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        examples = [MSMarcoExample(**json.loads(line)) for line in f if line.strip()]

    generator = GeneratorService()
    generator.retrieval_service._ensure_loaded()

    # Warm-up embedding service to measure true warm generation overhead
    print("Warming up embedding service & PyTorch runtime...")
    generator.retrieval_service.retrieve(AskRequest(query="Warmup query", top_k=10))

    provider_name = generator.llm_provider.__class__.__name__ if generator.llm_provider else "Default (Configured)"
    print(f"Active Provider: {provider_name}")

    status_counts: Dict[str, int] = {}
    g_scores = []
    ret_latencies = []
    prompt_latencies = []
    llm_latencies = []
    gen_latencies = []
    verify_latencies = []
    guard_latencies = []
    total_latencies = []
    token_counts = []

    # Separate English vs Indic tracking
    en_latencies = []
    indic_latencies = []
    en_status: Dict[str, int] = {}
    indic_status: Dict[str, int] = {}

    start_time = time.perf_counter()
    num_evals = 0

    # Evaluate 100 representative examples (English source queries + Indic target queries across languages)
    # Using top_k=10 as established in Phase 9 recommended configuration
    sample_sub = examples[::14]

    for ex in sample_sub:
        target_lang = ex.target_lang or "en"
        ask_req = AskRequest(query=ex.query, top_k=10, preferred_answer_language=target_lang)
        resp = generator.generate_answer(ask_req)

        st_val = resp.grounding_status.value
        status_counts[st_val] = status_counts.get(st_val, 0) + 1
        g_scores.append(resp.grounding_score)
        ret_latencies.append(resp.retrieval_latency_ms)
        prompt_latencies.append(resp.prompt_construction_latency_ms)
        llm_latencies.append(resp.llm_request_latency_ms)
        gen_latencies.append(resp.generation_latency_ms)
        verify_latencies.append(resp.verification_latency_ms)
        guard_latencies.append(resp.guardrail_latency_ms)
        total_latencies.append(resp.total_latency_ms)
        if resp.output_token_count is not None:
            token_counts.append(resp.output_token_count)

        if target_lang == "en" or ex.source_lang == "en":
            en_latencies.append(resp.total_latency_ms)
            en_status[st_val] = en_status.get(st_val, 0) + 1
        else:
            indic_latencies.append(resp.total_latency_ms)
            indic_status[st_val] = indic_status.get(st_val, 0) + 1

        num_evals += 1

    total_duration = time.perf_counter() - start_time

    print(f"\nEvaluated {num_evals} representative RAG generation requests in {total_duration:.2f} s.")

    print("\n--- 1. Grounding Verification & Reliability Status Rates ---")
    grounded_cnt = status_counts.get(GroundingStatus.GROUNDED.value, 0)
    part_cnt = status_counts.get(GroundingStatus.PARTIALLY_GROUNDED.value, 0)
    ungrounded_cnt = status_counts.get(GroundingStatus.UNGROUNDED.value, 0)
    error_cnt = status_counts.get(GroundingStatus.PROVIDER_ERROR.value, 0) + status_counts.get(GroundingStatus.PROVIDER_TIMEOUT.value, 0)
    no_ctx_cnt = status_counts.get(GroundingStatus.NO_CONTEXT.value, 0) + status_counts.get(GroundingStatus.LOW_CONFIDENCE.value, 0)

    print(f"  Grounded Rate (Fully)       : {grounded_cnt:>3} ({grounded_cnt/num_evals*100:>5.1f}%)")
    print(f"  Partially Grounded Rate     : {part_cnt:>3} ({part_cnt/num_evals*100:>5.1f}%)")
    print(f"  Ungrounded Rate             : {ungrounded_cnt:>3} ({ungrounded_cnt/num_evals*100:>5.1f}%)")
    print(f"  No Context / Low Confidence : {no_ctx_cnt:>3} ({no_ctx_cnt/num_evals*100:>5.1f}%)")
    print(f"  Provider Errors / Timeouts  : {error_cnt:>3} ({error_cnt/num_evals*100:>5.1f}%)")

    print("\n--- 2. Latency Component Breakdown (Mean ms) ---")
    print(f"  1. Retrieval Latency        : {np.mean(ret_latencies):>7.2f} ms")
    print(f"  2. Prompt Construction      : {np.mean(prompt_latencies):>7.2f} ms")
    print(f"  3. LLM Request / Network    : {np.mean(llm_latencies):>7.2f} ms")
    print(f"  4. Generation Latency       : {np.mean(gen_latencies):>7.2f} ms")
    print(f"  5. Verification Latency     : {np.mean(verify_latencies):>7.2f} ms")
    print(f"  6. Total Guardrail Overhead : {np.mean(guard_latencies):>7.2f} ms")
    print(f"  7. Total /ask Latency       : {np.mean(total_latencies):>7.2f} ms")

    if token_counts:
        print(f"\n--- 3. Output Token Count Metrics ---")
        print(f"  Mean Output Token Count     : {np.mean(token_counts):>7.1f} tokens")
        print(f"  P50 Output Token Count      : {np.percentile(token_counts, 50):>7.1f} tokens")
        print(f"  Max Output Token Count      : {np.max(token_counts):>7d} tokens")

    print("\n--- 4. Percentile Latency Distribution (Total /ask Pipeline) ---")
    print(f"  P50 Latency (Median)        : {np.percentile(total_latencies, 50):>7.2f} ms")
    print(f"  P70 Latency                 : {np.percentile(total_latencies, 70):>7.2f} ms")
    print(f"  P95 Latency                 : {np.percentile(total_latencies, 95):>7.2f} ms")
    print(f"  P100 / Max Latency          : {np.max(total_latencies):>7.2f} ms")

    print("\n--- 5. English vs Indic Performance Comparison ---")
    if en_latencies:
        print(f"  English Queries ({len(en_latencies)}):")
        print(f"    Mean Latency              : {np.mean(en_latencies):>7.2f} ms")
        print(f"    P50 Latency               : {np.percentile(en_latencies, 50):>7.2f} ms")
        print(f"    P95 Latency               : {np.percentile(en_latencies, 95):>7.2f} ms")
    if indic_latencies:
        print(f"  Indic Language Queries ({len(indic_latencies)}):")
        print(f"    Mean Latency              : {np.mean(indic_latencies):>7.2f} ms")
        print(f"    P50 Latency               : {np.percentile(indic_latencies, 50):>7.2f} ms")
        print(f"    P95 Latency               : {np.percentile(indic_latencies, 95):>7.2f} ms")

    print("=" * 95)


if __name__ == "__main__":
    run_generation_quality_benchmark()
