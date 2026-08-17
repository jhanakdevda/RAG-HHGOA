"""
Phase 5A: GroundingVerifier Fine-Grained Latency Profiler & Optimization Script
Measures cold-start vs warm execution components of GroundingVerifier.
"""

import os
import sys
import time
import numpy as np
from typing import List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.chunk import TextChunk
from app.rag.embeddings import EmbeddingService
from app.rag.guardrails.verifier import GroundingVerifier, GroundingStatus


def run_verifier_profiling():
    print("=" * 90, flush=True)
    print("PHASE 5A — GROUNDING VERIFIER FINE-GRAINED LATENCY PROFILING", flush=True)
    print("=" * 90, flush=True)

    # 1. Cold-start timing
    t_init_start = time.perf_counter()
    shared_emb = EmbeddingService()
    shared_emb._load_model()
    t_init = (time.perf_counter() - t_init_start) * 1000.0
    print(f"Cold-Start Model & Tokenizer Load Time : {t_init:7.2f} ms", flush=True)

    verifier = GroundingVerifier(embedding_service=shared_emb)

    sample_chunks = [
        TextChunk(
            chunk_id="chk_001",
            query_id=100,
            text="Eagles are large, powerfully built birds of prey, with heavy heads and beaks. Most eagles fly at speeds between 30 and 55 miles per hour.",
            passage_index=0,
            chunk_index=0,
            char_count=146,
            word_count=26,
            language_code="en"
        ),
        TextChunk(
            chunk_id="chk_002",
            query_id=100,
            text="The bald eagle can reach diving speeds of up to 100 miles per hour when pursuing fish.",
            passage_index=0,
            chunk_index=1,
            char_count=87,
            word_count=16,
            language_code="en"
        )
    ]

    sample_answers = [
        "Eagles are large birds of prey that fly at speeds between 30 and 55 mph.",
        "The bald eagle dives at speeds up to 100 mph to catch fish.",
        "चील 30 से 55 मील प्रति घंटे की गति से उड़ती है।",
        "Eagles can travel at 300 miles per hour in normal flight."
    ]

    # Warm-up call
    _, _, _ = verifier.verify(sample_answers[0], sample_chunks)

    num_runs = 20
    t_split_list = []
    t_ctx_enc_list = []
    t_sent_enc_list = []
    t_sim_calc_list = []
    t_total_list = []
    scores = []
    statuses = []

    print(f"Executing {num_runs} warm GroundingVerifier profiling iterations...\n", flush=True)

    for i in range(num_runs):
        ans = sample_answers[i % len(sample_answers)]

        t0 = time.perf_counter()

        # Step A: Sentence splitting
        t_split_start = time.perf_counter()
        sentences = verifier._split_into_sentences(ans)
        combined_context = " ".join([c.text for c in sample_chunks])
        t_split = (time.perf_counter() - t_split_start) * 1000.0

        # Step B: Context encoding
        t_ctx_start = time.perf_counter()
        ctx_vec = shared_emb.encode_query(combined_context[:500], normalize=True)
        t_ctx_enc = (time.perf_counter() - t_ctx_start) * 1000.0

        # Step C: Sentence batch encoding
        t_sent_start = time.perf_counter()
        s_vecs = shared_emb.encode_texts(sentences, batch_size=len(sentences), normalize=True)
        t_sent_enc = (time.perf_counter() - t_sent_start) * 1000.0

        # Step D: Similarity calculation
        t_sim_start = time.perf_counter()
        sentence_scores = []
        for idx, s in enumerate(sentences):
            overlap_score = verifier._compute_word_overlap(s, combined_context)
            if ctx_vec is not None and s_vecs is not None and len(s_vecs) > idx:
                sem_sim = float(np.dot(s_vecs[idx], ctx_vec[0]))
            else:
                sem_sim = overlap_score
            s_score = max(overlap_score * 0.4 + sem_sim * 0.6, overlap_score)
            sentence_scores.append(s_score)

        avg_score = float(np.mean(sentence_scores)) if sentence_scores else 0.0
        g_score = round(max(0.0, min(1.0, avg_score)), 4)
        t_sim_calc = (time.perf_counter() - t_sim_start) * 1000.0

        t_total = (time.perf_counter() - t0) * 1000.0

        # Run full verify for validation
        _, status, full_score = verifier.verify(ans, sample_chunks)

        t_split_list.append(t_split)
        t_ctx_enc_list.append(t_ctx_enc)
        t_sent_enc_list.append(t_sent_enc)
        t_sim_calc_list.append(t_sim_calc)
        t_total_list.append(t_total)
        scores.append(full_score)
        statuses.append(status.value)

    print("=" * 90, flush=True)
    print("WARM GROUNDING VERIFIER COMPONENT TIMING BREAKDOWN (20 ITERATIONS)", flush=True)
    print("=" * 90, flush=True)
    header = f"{'Component':<32} | {'P50 (ms)':<9} | {'P70 (ms)':<9} | {'P95 (ms)':<9} | {'Mean (ms)':<9}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    comps = {
        "Sentence Splitting": t_split_list,
        "Context Encoding (1 vector)": t_ctx_enc_list,
        "Sentence Batch Enc (N vectors)": t_sent_enc_list,
        "Similarity & Score Calc": t_sim_calc_list,
        "Total Warm Verifier Latency": t_total_list
    }

    for name, vals in comps.items():
        arr = np.array(vals)
        print(f"{name:<32} | {np.percentile(arr, 50):9.2f} | {np.percentile(arr, 70):9.2f} | {np.percentile(arr, 95):9.2f} | {np.mean(arr):9.2f}", flush=True)

    print("=" * 90, flush=True)
    print(f"VERIFIER DECISION VERIFICATION:", flush=True)
    print(f"Sample Grounding Scores : {scores[:4]}", flush=True)
    print(f"Sample Public Statuses  : {statuses[:4]}", flush=True)
    print("=" * 90, flush=True)


if __name__ == "__main__":
    run_verifier_profiling()
