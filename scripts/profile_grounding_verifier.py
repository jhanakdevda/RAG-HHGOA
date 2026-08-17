"""
GroundingVerifier Fine-Grained Internal Timing Profiler

Measures component-level latency of GroundingVerifier on the warm path:
- Sentence splitting time
- Lexical word overlap scoring
- Sentence tokenization & model inference
- Context tokenization & model inference (repeated per sentence)
- Vector dot-product / scoring
- Python overhead & total verifier execution time
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict

# Force UTF-8 stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.chunk import TextChunk
from app.rag.guardrails.verifier import GroundingVerifier, InternalVerificationState
from app.models.generation import GroundingStatus


def run_profiler():
    print("=" * 90)
    print("GroundingVerifier Internal Micro-Profiling")
    print("=" * 90)

    verifier = GroundingVerifier()

    # Representative test case matching the warm benchmark
    chunks = [
        TextChunk(
            chunk_id="165349_p3_c2",
            query_id=165349,
            passage_index=3,
            chunk_index=2,
            char_count=200,
            word_count=35,
            language_code="hi",
            language_name="Hindi",
            source_lang="en",
            target_lang="hi",
            text="पणजी भारत के गोवा राज्य की राजधानी है। यह मांडवी नदी के तट पर स्थित एक खूबसूरत शहर है।"
        ),
        TextChunk(
            chunk_id="165349_p3_c3",
            query_id=165349,
            passage_index=3,
            chunk_index=3,
            char_count=180,
            word_count=30,
            language_code="en",
            language_name="English",
            source_lang="en",
            target_lang="en",
            text="Panaji is the capital of the Indian state of Goa. It lies on the banks of the Mandovi River estuary."
        )
    ]

    answer_text = "Panaji is the capital of Goa. It is located on the banks of the Mandovi River. Goa is a coastal state in India."

    # Cold-start call to ensure model weights and PyTorch runtime are warm
    print("Executing cold-start call to warm up PyTorch model weights...")
    verifier.verify(answer_text, chunks)
    print("Warm-up complete.\n")

    num_runs = 10
    total_times = []
    sentence_split_times = []
    lexical_overlap_times = []
    sent_encode_times = []
    ctx_encode_times = []
    scoring_times = []

    # Model component timing details per encode call
    tokenizer_times = []
    forward_pass_times = []
    normalization_times = []

    for _ in range(num_runs):
        # Step 1: Sentence Splitting
        t_split0 = time.perf_counter()
        combined_context = " ".join([c.text for c in chunks])
        sentences = verifier._split_into_sentences(answer_text)
        t_split1 = time.perf_counter()
        sentence_split_times.append((t_split1 - t_split0) * 1000.0)

        run_lexical = 0.0
        run_sent_enc = 0.0
        run_ctx_enc = 0.0
        run_scoring = 0.0

        for s in sentences:
            # Step 2: Lexical Overlap
            t_lex0 = time.perf_counter()
            overlap_score = verifier._compute_word_overlap(s, combined_context)
            t_lex1 = time.perf_counter()
            run_lexical += (t_lex1 - t_lex0) * 1000.0

            # Step 3: Sentence Embedding
            t_s0 = time.perf_counter()
            s_vec = verifier.embedding_service.encode_query(s, normalize=True)
            t_s1 = time.perf_counter()
            run_sent_enc += (t_s1 - t_s0) * 1000.0

            # Step 4: Context Embedding (REPEATED per sentence in verifier.py)
            t_c0 = time.perf_counter()
            ctx_vec = verifier.embedding_service.encode_query(combined_context[:500], normalize=True)
            t_c1 = time.perf_counter()
            run_ctx_enc += (t_c1 - t_c0) * 1000.0

            # Step 5: Dot Product & Scoring
            t_sc0 = time.perf_counter()
            sem_sim = float(np.dot(s_vec[0], ctx_vec[0]))
            s_score = max(overlap_score * 0.4 + sem_sim * 0.6, overlap_score)
            t_sc1 = time.perf_counter()
            run_scoring += (t_sc1 - t_sc0) * 1000.0

        # Full verifier execution timing
        t_v0 = time.perf_counter()
        state, status, g_score = verifier.verify(answer_text, chunks)
        t_v1 = time.perf_counter()
        total_times.append((t_v1 - t_v0) * 1000.0)

        lexical_overlap_times.append(run_lexical)
        sent_encode_times.append(run_sent_enc)
        ctx_encode_times.append(run_ctx_enc)
        scoring_times.append(run_scoring)

    # Detailed Transformer Sub-Operation Profiling (Tokenization vs Forward Pass vs Normalization)
    emb_service = verifier.embedding_service
    emb_service._load_model()
    st_model = emb_service._model
    sample_sentence = sentences[0]

    import torch
    for _ in range(10):
        # 1. Tokenizer time
        t_tok0 = time.perf_counter()
        features = st_model.tokenize([sample_sentence])
        t_tok1 = time.perf_counter()
        tokenizer_times.append((t_tok1 - t_tok0) * 1000.0)

        # Move tensors
        features = {k: v.to(st_model.device) if hasattr(v, "to") else v for k, v in features.items()}

        # 2. Forward pass time
        t_fwd0 = time.perf_counter()
        with torch.inference_mode():
            out = st_model(features)
            raw_emb = out["sentence_embedding"].cpu().numpy()
        t_fwd1 = time.perf_counter()
        forward_pass_times.append((t_fwd1 - t_fwd0) * 1000.0)

        # 3. Normalization time
        t_norm0 = time.perf_counter()
        norms = np.linalg.norm(raw_emb, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        _ = raw_emb / norms
        t_norm1 = time.perf_counter()
        normalization_times.append((t_norm1 - t_norm0) * 1000.0)

    mean_total = float(np.mean(total_times))
    mean_split = float(np.mean(sentence_split_times))
    mean_lexical = float(np.mean(lexical_overlap_times))
    mean_sent_enc = float(np.mean(sent_encode_times))
    mean_ctx_enc = float(np.mean(ctx_encode_times))
    mean_scoring = float(np.mean(scoring_times))

    sum_sub = mean_split + mean_lexical + mean_sent_enc + mean_ctx_enc + mean_scoring
    mean_python_overhead = max(0.0, mean_total - sum_sub)

    mean_tok = float(np.mean(tokenizer_times))
    mean_fwd = float(np.mean(forward_pass_times))
    mean_norm = float(np.mean(normalization_times))

    print(f"Evaluated GroundingVerifier over {num_runs} warm runs for candidate answer with {len(sentences)} sentences.")
    print(f"Warm Path Median (P50) Total Verifier Latency : {np.percentile(total_times, 50):.2f} ms")
    print(f"Warm Path Mean Total Verifier Latency        : {mean_total:.2f} ms")
    print("\n" + "=" * 90)
    print(f"{'Component / Sub-Operation':<42} | {'Mean Time (ms)':<15} | {'% of Total Latency':<20}")
    print("=" * 90)
    print(f"{'1. Sentence Splitting (_split_into_sentences)':<42} | {mean_split:>13.2f} ms | {mean_split/mean_total*100:>18.1f}%")
    print(f"{'2. Lexical Word Overlap (_compute_word_overlap)':<42} | {mean_lexical:>13.2f} ms | {mean_lexical/mean_total*100:>18.1f}%")
    print(f"{'3. Sentence Embedding (encode_query per sent)':<42} | {mean_sent_enc:>13.2f} ms | {mean_sent_enc/mean_total*100:>18.1f}%")
    print(f"{'4. Context Embedding (REPEATED per sentence)':<42} | {mean_ctx_enc:>13.2f} ms | {mean_ctx_enc/mean_total*100:>18.1f}%")
    print(f"{'5. Dot Product & Score Calculation':<42} | {mean_scoring:>13.2f} ms | {mean_scoring/mean_total*100:>18.1f}%")
    print(f"{'6. Other Python Overhead / Glue':<42} | {mean_python_overhead:>13.2f} ms | {mean_python_overhead/mean_total*100:>18.1f}%")
    print("-" * 90)
    print(f"{'TOTAL WARM VERIFIER LATENCY':<42} | {mean_total:>13.2f} ms | {'100.0%':>18}")
    print("=" * 90)

    print("\n--- Transformer Model Sub-Operation Breakdown (per single encode_query call) ---")
    print(f"  - Tokenizer Latency                  : {mean_tok:.3f} ms ({mean_tok/(mean_tok+mean_fwd+mean_norm)*100:.1f}%)")
    print(f"  - PyTorch Model Forward Pass         : {mean_fwd:.3f} ms ({mean_fwd/(mean_tok+mean_fwd+mean_norm)*100:.1f}%)")
    print(f"  - Vector Normalization               : {mean_norm:.3f} ms ({mean_norm/(mean_tok+mean_fwd+mean_norm)*100:.1f}%)")
    print(f"  - Single Pass Total                  : {mean_tok + mean_fwd + mean_norm:.3f} ms")
    print(f"  - Total Encode Pass Count            : 6 passes (3 sentence + 3 repeated context passes)")
    print("=" * 90)


if __name__ == "__main__":
    run_profiler()
