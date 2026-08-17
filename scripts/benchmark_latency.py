"""
Phase 9 — RAG Pipeline Controlled Concurrency & Latency Benchmarking Script

Measures cold-start model load timing, warm request timings across components,
and controlled concurrency benchmarks (1, 5, and 10 concurrent requests).
Separates local RAG operations from external LLM provider API latencies.
"""

import os
import sys
import time
import concurrent.futures
import numpy as np

# Force UTF-8 stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.generation import AskRequest
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import FAISSVectorStore
from app.rag.retrieval import RetrievalService
from app.rag.generator import GeneratorService


def benchmark_cold_start():
    print("\n--- 1. Embedding Model Cold-Start & Load Time Benchmark ---")
    start_load = time.perf_counter()
    embedder = EmbeddingService()
    dim = embedder.dimension
    load_ms = (time.perf_counter() - start_load) * 1000.0

    print(f"  Embedding Model Loaded : sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    print(f"  Vector Dimension       : {dim}")
    print(f"  Cold-Start Load Time   : {load_ms:.2f} ms")


def benchmark_component_breakdown():
    print("\n--- 2. Isolated Pipeline Component Latency Benchmark (100 Iterations) ---")

    retrieval_service = RetrievalService()
    retrieval_service._ensure_loaded()

    sample_query = "What is the capital of Goa?"
    n_iters = 50

    embed_times = []
    faiss_times = []
    meta_times = []

    for _ in range(n_iters):
        # Embedding
        t0 = time.perf_counter()
        q_vec = retrieval_service.embedding_service.encode_query(sample_query, normalize=True)
        t_embed = (time.perf_counter() - t0) * 1000.0
        embed_times.append(t_embed)

        # FAISS
        t1 = time.perf_counter()
        distances, indices = retrieval_service.vector_store.search(q_vec, top_k=5)
        t_faiss = (time.perf_counter() - t1) * 1000.0
        faiss_times.append(t_faiss)

        # Metadata
        t2 = time.perf_counter()
        meta_records = [retrieval_service._metadata_cache[idx] for idx in indices[0] if idx >= 0]
        t_meta = (time.perf_counter() - t2) * 1000.0
        meta_times.append(t_meta)

    print(f"  Query Embedding Latency : Mean: {np.mean(embed_times):.2f} ms | P95: {np.percentile(embed_times, 95):.2f} ms")
    print(f"  FAISS Vector Search     : Mean: {np.mean(faiss_times):.2f} ms | P95: {np.percentile(faiss_times, 95):.2f} ms")
    print(f"  Metadata Lookup         : Mean: {np.mean(meta_times):.2f} ms | P95: {np.percentile(meta_times, 95):.2f} ms")
    print(f"  Local RAG Total (Mean)  : {np.mean(embed_times) + np.mean(faiss_times) + np.mean(meta_times):.2f} ms (< 200 ms target)")


def benchmark_concurrency():
    print("\n--- 3. Controlled Concurrency Benchmarks (1, 5, 10 Concurrent Requests) ---")

    generator = GeneratorService()
    queries = [
        "What is the capital of Goa?",
        "गोवा की राजधानी क्या है?",
        "गोव्याची राजधानी कोणती आहे?",
        "গোয়ার राजधानी কী?",
        "கோவாவின் தலைநகரம் எது?",
        "గోవా రాజధాని ఏది?",
        "گوا کا دارالحکومت کون سا ہے؟",
        "What is the population of Goa?",
        "गोवा का मौसम कैसा है?",
        "गोवा किस राज्य में है?"
    ]

    for concurrency in [1, 5, 10]:
        start_conc = time.perf_counter()
        total_latencies = []

        def worker(q_str):
            req = AskRequest(query=q_str, top_k=3)
            resp = generator.generate_answer(req)
            return resp.total_latency_ms

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker, queries[i % len(queries)]) for i in range(concurrency * 2)]
            for f in concurrent.futures.as_completed(futures):
                total_latencies.append(f.result())

        total_wall_ms = (time.perf_counter() - start_conc) * 1000.0
        print(f"  Concurrency Level {concurrency:<2} : Total Wall Time: {total_wall_ms:.2f} ms | Avg Req Latency: {np.mean(total_latencies):.2f} ms | P95: {np.percentile(total_latencies, 95):.2f} ms")


def run_latency_benchmark():
    print("=" * 85)
    print("Phase 9 — Precision Latency & Concurrency Benchmarking")
    print("=" * 85)

    benchmark_cold_start()
    benchmark_component_breakdown()
    benchmark_concurrency()

    print("\n" + "=" * 85)
    print("Latency & Concurrency Benchmarking Complete")
    print("=" * 85)


if __name__ == "__main__":
    run_latency_benchmark()
