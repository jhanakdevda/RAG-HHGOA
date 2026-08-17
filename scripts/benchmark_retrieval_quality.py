"""
Phase 9 Optimization — Retrieval Quality & Candidate Top-K Tuning Benchmark

Evaluates dense retrieval relevance (Recall@1, Recall@3, Recall@5, Recall@10, Recall@20)
and candidate top-k window impact across the 1,400 authentic MS MARCO-XI ground-truth dataset
(21,573 FAISS vectors) across 14 Indic target languages + English.
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
from app.models.retrieval import RetrievalRequest
from app.rag.retrieval import RetrievalService

SAMPLE_PATH = os.path.join("data", "sample", "msmarco_xi_expanded_sample.jsonl")


def load_expanded_examples() -> List[MSMarcoExample]:
    path = SAMPLE_PATH
    if not os.path.exists(path):
        path = os.path.join("..", SAMPLE_PATH)

    examples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(MSMarcoExample(**json.loads(line)))
    return examples


def run_retrieval_benchmark():
    print("=" * 100)
    print("Step 4 — Expanded MS MARCO-XI Ground-Truth Retrieval Quality Benchmark (1,400 GT Records)")
    print("=" * 100)

    examples = load_expanded_examples()
    num_records = len(examples)
    print(f"Loaded {num_records} authentic ground-truth MS MARCO-XI records.")

    retrieval_service = RetrievalService()
    retrieval_service._ensure_loaded()
    print(f"FAISS Vector Store Loaded: {retrieval_service.vector_store.ntotal} vectors indexed.")

    lang_stats: Dict[str, Dict] = {}

    def init_lang(code, name):
        if code not in lang_stats:
            lang_stats[code] = {
                "name": name,
                "total": 0,
                "h1": 0, "h3": 0, "h5": 0, "h10": 0, "h20": 0,
                "scores": []
            }

    tot_queries = 0
    h1_tot = 0
    h3_tot = 0
    h5_tot = 0
    h10_tot = 0
    h20_tot = 0
    all_scores = []

    start_time = time.perf_counter()

    for ex in examples:
        target_lang = ex.target_lang or "en"
        target_lang_name = ex.language_name or target_lang

        init_lang(target_lang, target_lang_name)
        init_lang("en", "English")

        selected_p_indices = [i for i, sel in enumerate(ex.passages.is_selected) if sel == 1]

        # 1. Target Indic Query Evaluation (Top-20 window)
        ret_req_target = RetrievalRequest(query=ex.query, top_k=20, language_filter=target_lang)
        ret_resp_target = retrieval_service.retrieve(ret_req_target)
        ret_indices_t = [res.chunk.passage_index for res in ret_resp_target.results]

        lang_stats[target_lang]["total"] += 1
        tot_queries += 1

        hit1_t = any(p in selected_p_indices for p in ret_indices_t[:1])
        hit3_t = any(p in selected_p_indices for p in ret_indices_t[:3])
        hit5_t = any(p in selected_p_indices for p in ret_indices_t[:5])
        hit10_t = any(p in selected_p_indices for p in ret_indices_t[:10])
        hit20_t = any(p in selected_p_indices for p in ret_indices_t[:20])

        if hit1_t: lang_stats[target_lang]["h1"] += 1; h1_tot += 1
        if hit3_t: lang_stats[target_lang]["h3"] += 1; h3_tot += 1
        if hit5_t: lang_stats[target_lang]["h5"] += 1; h5_tot += 1
        if hit10_t: lang_stats[target_lang]["h10"] += 1; h10_tot += 1
        if hit20_t: lang_stats[target_lang]["h20"] += 1; h20_tot += 1

        lang_stats[target_lang]["scores"].extend([r.score for r in ret_resp_target.results])
        all_scores.extend([r.score for r in ret_resp_target.results])

        # 2. Source English Query Evaluation (Top-20 window)
        eng_q = ex.Eng_Query or ex.query
        ret_req_eng = RetrievalRequest(query=eng_q, top_k=20, language_filter=None)
        ret_resp_eng = retrieval_service.retrieve(ret_req_eng)
        ret_indices_e = [res.chunk.passage_index for res in ret_resp_eng.results]

        lang_stats["en"]["total"] += 1
        tot_queries += 1

        hit1_e = any(p in selected_p_indices for p in ret_indices_e[:1])
        hit3_e = any(p in selected_p_indices for p in ret_indices_e[:3])
        hit5_e = any(p in selected_p_indices for p in ret_indices_e[:5])
        hit10_e = any(p in selected_p_indices for p in ret_indices_e[:10])
        hit20_e = any(p in selected_p_indices for p in ret_indices_e[:20])

        if hit1_e: lang_stats["en"]["h1"] += 1; h1_tot += 1
        if hit3_e: lang_stats["en"]["h3"] += 1; h3_tot += 1
        if hit5_e: lang_stats["en"]["h5"] += 1; h5_tot += 1
        if hit10_e: lang_stats["en"]["h10"] += 1; h10_tot += 1
        if hit20_e: lang_stats["en"]["h20"] += 1; h20_tot += 1

        lang_stats["en"]["scores"].extend([r.score for r in ret_resp_eng.results])
        all_scores.extend([r.score for r in ret_resp_eng.results])

    duration = time.perf_counter() - start_time

    print("\n" + "=" * 100)
    print("Expanded Benchmark Overall Relevance Summary")
    print("=" * 100)
    print(f"Total Authentic GT Records        : {num_records}")
    print(f"Total Evaluated Ground-Truth Queries: {tot_queries} (1,400 English Source + 1,400 Indic Target)")
    print(f"Overall Recall@1  (Top-1 Relevance) : {(h1_tot/tot_queries)*100.0:.2f}% ({h1_tot}/{tot_queries})")
    print(f"Overall Recall@3  (Top-3 Relevance) : {(h3_tot/tot_queries)*100.0:.2f}% ({h3_tot}/{tot_queries})")
    print(f"Overall Recall@5  (Top-5 Relevance) : {(h5_tot/tot_queries)*100.0:.2f}% ({h5_tot}/{tot_queries})")
    print(f"Overall Recall@10 (Top-10 Relevance): {(h10_tot/tot_queries)*100.0:.2f}% ({h10_tot}/{tot_queries})")
    print(f"Overall Recall@20 (Top-20 Relevance): {(h20_tot/tot_queries)*100.0:.2f}% ({h20_tot}/{tot_queries})")
    print(f"Total Evaluation Duration           : {duration:.2f} seconds")

    print("\n" + "=" * 100)
    print("Language Breakdown (Raw Hits, Denominators & Recalls)")
    print("=" * 100)
    print(f"{'Category':<16} | {'Language':<12} | {'Code':<8} | {'Queries':<7} | {'H1':<4} | {'H3':<4} | {'H5':<4} | {'H10':<4} | {'R@1':<7} | {'R@3':<7} | {'R@5':<7} | {'R@10':<7}")
    print("-" * 100)

    # Print Source English first
    if "en" in lang_stats:
        st_e = lang_stats["en"]
        c_e = st_e["total"]
        r1_e = (st_e["h1"] / c_e) * 100.0
        r3_e = (st_e["h3"] / c_e) * 100.0
        r5_e = (st_e["h5"] / c_e) * 100.0
        r10_e = (st_e["h10"] / c_e) * 100.0
        print(f"{'Source Language':<16} | {'English':<12} | {'en':<8} | {c_e:<7} | {st_e['h1']:<4} | {st_e['h3']:<4} | {st_e['h5']:<4} | {st_e['h10']:<4} | {r1_e:>6.1f}% | {r3_e:>6.1f}% | {r5_e:>6.1f}% | {r10_e:>6.1f}%")
        print("-" * 100)

    # Indic languages
    for code, st in sorted(lang_stats.items()):
        if code == "en": continue
        c = st["total"]
        r1 = (st["h1"] / c) * 100.0
        r3 = (st["h3"] / c) * 100.0
        r5 = (st["h5"] / c) * 100.0
        r10 = (st["h10"] / c) * 100.0
        print(f"{'Target Language':<16} | {st['name']:<12} | {code:<8} | {c:<7} | {st['h1']:<4} | {st['h3']:<4} | {st['h5']:<4} | {st['h10']:<4} | {r1:>6.1f}% | {r3:>6.1f}% | {r5:>6.1f}% | {r10:>6.1f}%")

    print("=" * 100)


if __name__ == "__main__":
    run_retrieval_benchmark()
