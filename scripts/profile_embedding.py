"""
Phase 9 Optimization — Embedding Latency Profiler & PyTorch Thread Optimization

Profiles sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2:
1. Cold-start model load time
2. Warm single-query p50, p95, p99 latency
3. Batch size 1, 8, 16 latency
4. Component breakdown (Tokenizer vs PyTorch Model Inference vs L2 Normalization)
5. Optimized PyTorch configuration (torch.set_num_threads, torch.inference_mode)
"""

import os
import sys
import time
import numpy as np
import torch

# Force UTF-8 stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.rag.embeddings import EmbeddingService


def run_embedding_profiler():
    print("=" * 90)
    print("Step 2 & 3 — Embedding Latency Profiling & PyTorch Optimization Benchmark")
    print("=" * 90)

    # 1. Cold-Start Model Load Timing
    t0 = time.perf_counter()
    embedder = EmbeddingService()
    dim = embedder.dimension
    t_cold_ms = (time.perf_counter() - t0) * 1000.0

    print(f"  Model Loaded          : {embedder.model_name}")
    print(f"  Vector Dimension      : {dim}")
    print(f"  Cold-Start Load Time  : {t_cold_ms:.2f} ms")

    sample_query = "What is the capital of Goa?"
    sample_queries_8 = [sample_query] * 8
    sample_queries_16 = [sample_query] * 16

    # 2. Warm Single-Query & Batch Benchmarks (Unoptimized baseline)
    single_latencies = []
    for _ in range(50):
        t_start = time.perf_counter()
        _ = embedder.encode_query(sample_query)
        single_latencies.append((time.perf_counter() - t_start) * 1000.0)

    p50_base = float(np.percentile(single_latencies, 50))
    p95_base = float(np.percentile(single_latencies, 95))
    p99_base = float(np.percentile(single_latencies, 99))

    print("\n--- Unoptimized Warm Latency Baseline ---")
    print(f"  Single Query (Batch 1) p50 : {p50_base:.2f} ms")
    print(f"  Single Query (Batch 1) p95 : {p95_base:.2f} ms")
    print(f"  Single Query (Batch 1) p99 : {p99_base:.2f} ms")

    # Batch Size 8 & 16
    t_b8_start = time.perf_counter()
    _ = embedder.encode_texts(sample_queries_8, batch_size=8)
    b8_ms = (time.perf_counter() - t_b8_start) * 1000.0

    t_b16_start = time.perf_counter()
    _ = embedder.encode_texts(sample_queries_16, batch_size=16)
    b16_ms = (time.perf_counter() - t_b16_start) * 1000.0

    print(f"  Batch Size 8 Total Latency : {b8_ms:.2f} ms ({b8_ms/8.0:.2f} ms/query)")
    print(f"  Batch Size 16 Total Latency: {b16_ms:.2f} ms ({b16_ms/16.0:.2f} ms/query)")

    # 3. Component Breakdown Profiling
    print("\n--- Component Execution Breakdown ---")
    model_obj = embedder._model

    t_tok_start = time.perf_counter()
    tokens = model_obj.tokenize([sample_query])
    t_tok_ms = (time.perf_counter() - t_tok_start) * 1000.0

    t_inf_start = time.perf_counter()
    with torch.no_grad():
        out = model_obj(tokens)
        features = out['sentence_embedding']
    t_inf_ms = (time.perf_counter() - t_inf_start) * 1000.0

    t_norm_start = time.perf_counter()
    vec = features.detach().cpu().numpy()
    vec = vec / np.linalg.norm(vec, axis=1, keepdims=True)
    t_norm_ms = (time.perf_counter() - t_norm_start) * 1000.0

    print(f"  Tokenization Time          : {t_tok_ms:.2f} ms")
    print(f"  PyTorch Model Forward Pass : {t_inf_ms:.2f} ms")
    print(f"  NumPy Detach & L2 Norm     : {t_norm_ms:.2f} ms")

    # 4. PyTorch Thread & Inference Mode Optimization
    print("\n--- Optimized PyTorch Execution Benchmark ---")

    # Set PyTorch thread count to 4 for optimal CPU execution
    torch.set_num_threads(4)

    opt_latencies = []
    for _ in range(50):
        t_opt_start = time.perf_counter()
        with torch.inference_mode():
            _ = embedder.encode_query(sample_query)
        opt_latencies.append((time.perf_counter() - t_opt_start) * 1000.0)

    p50_opt = float(np.percentile(opt_latencies, 50))
    p95_opt = float(np.percentile(opt_latencies, 95))
    p99_opt = float(np.percentile(opt_latencies, 99))

    print(f"  Optimized Single Query p50 : {p50_opt:.2f} ms (vs Baseline: {p50_base:.2f} ms)")
    print(f"  Optimized Single Query p95 : {p95_opt:.2f} ms (vs Baseline: {p95_base:.2f} ms)")
    print(f"  Optimized Single Query p99 : {p99_opt:.2f} ms (vs Baseline: {p99_base:.2f} ms)")
    print(f"  Latency Reduction Ratio   : {((p50_base - p50_opt) / p50_base) * 100.0:.1f}% improvement")

    print("\n" + "=" * 90)
    print("Embedding Latency Profiling Complete")
    print("=" * 90)


if __name__ == "__main__":
    run_embedding_profiler()
