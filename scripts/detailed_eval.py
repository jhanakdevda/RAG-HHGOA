import os
import sys
import json
import numpy as np
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.dataset import MSMarcoExample
from app.models.retrieval import RetrievalRequest
from app.rag.retrieval import RetrievalService

sample_path = "data/sample/msmarco_xi_multilingual_sample.jsonl"
with open(sample_path, "r", encoding="utf-8") as f:
    examples = [MSMarcoExample(**json.loads(line)) for line in f if line.strip()]

retrieval_service = RetrievalService()

lang_metrics: Dict[str, Dict] = {}

def init_lang(code, name):
    if code not in lang_metrics:
        lang_metrics[code] = {
            "name": name,
            "total_queries": 0,
            "gt_queries": 0,  # Queries with is_selected == 1
            "hits1_full": 0,
            "hits3_full": 0,
            "hits5_full": 0,
            "scores": []
        }

for ex in examples:
    target_lang = ex.target_lang or "en"
    target_lang_name = ex.language_name or target_lang
    
    init_lang(target_lang, target_lang_name)
    init_lang("en", "English")

    selected_p_indices = [i for i, sel in enumerate(ex.passages.is_selected) if sel == 1]
    has_gt = len(selected_p_indices) > 0

    # 1. Target Indic Query Evaluation
    ret_req_target = RetrievalRequest(query=ex.query, top_k=5, language_filter=target_lang)
    ret_resp_target = retrieval_service.retrieve(ret_req_target)
    ret_indices_target = [res.chunk.passage_index for res in ret_resp_target.results]

    lang_metrics[target_lang]["total_queries"] += 1
    if has_gt:
        lang_metrics[target_lang]["gt_queries"] += 1

    h1_t = any(p in selected_p_indices for p in ret_indices_target[:1])
    h3_t = any(p in selected_p_indices for p in ret_indices_target[:3])
    h5_t = any(p in selected_p_indices for p in ret_indices_target[:5])

    if h1_t: lang_metrics[target_lang]["hits1_full"] += 1
    if h3_t: lang_metrics[target_lang]["hits3_full"] += 1
    if h5_t: lang_metrics[target_lang]["hits5_full"] += 1
    lang_metrics[target_lang]["scores"].extend([res.score for res in ret_resp_target.results])

    # 2. Source English Query Evaluation
    eng_q = ex.Eng_Query or ex.query
    ret_req_eng = RetrievalRequest(query=eng_q, top_k=5, language_filter=None)
    ret_resp_eng = retrieval_service.retrieve(ret_req_eng)
    ret_indices_eng = [res.chunk.passage_index for res in ret_resp_eng.results]

    lang_metrics["en"]["total_queries"] += 1
    if has_gt:
        lang_metrics["en"]["gt_queries"] += 1

    h1_e = any(p in selected_p_indices for p in ret_indices_eng[:1])
    h3_e = any(p in selected_p_indices for p in ret_indices_eng[:3])
    h5_e = any(p in selected_p_indices for p in ret_indices_eng[:5])

    if h1_e: lang_metrics["en"]["hits1_full"] += 1
    if h3_e: lang_metrics["en"]["hits3_full"] += 1
    if h5_e: lang_metrics["en"]["hits5_full"] += 1
    lang_metrics["en"]["scores"].extend([res.score for res in ret_resp_eng.results])

print("=" * 110)
print(f"{'Category':<16} | {'Language':<12} | {'Code':<8} | {'Total':<5} | {'GT':<4} | {'H1':<4} | {'H3':<4} | {'H5':<4} | {'Full R@1':<8} | {'Full R@3':<8} | {'Full R@5':<8} | {'Filtered R@5':<10}")
print("-" * 110)

tot_q = 0
tot_gt = 0
tot_h1 = 0
tot_h3 = 0
tot_h5 = 0

# Print English first
st_en = lang_metrics["en"]
tot_q += st_en["total_queries"]
tot_gt += st_en["gt_queries"]
tot_h1 += st_en["hits1_full"]
tot_h3 += st_en["hits3_full"]
tot_h5 += st_en["hits5_full"]
r1_e = (st_en["hits1_full"] / st_en["total_queries"]) * 100.0
r3_e = (st_en["hits3_full"] / st_en["total_queries"]) * 100.0
r5_e = (st_en["hits5_full"] / st_en["total_queries"]) * 100.0
fr5_e = (st_en["hits5_full"] / st_en["gt_queries"]) * 100.0 if st_en["gt_queries"] > 0 else 0.0
print(f"{'Source Language':<16} | {'English':<12} | {'en':<8} | {st_en['total_queries']:<5} | {st_en['gt_queries']:<4} | {st_en['hits1_full']:<4} | {st_en['hits3_full']:<4} | {st_en['hits5_full']:<4} | {r1_e:>7.1f}% | {r3_e:>7.1f}% | {r5_e:>7.1f}% | {fr5_e:>9.1f}%")
print("-" * 110)

# Indic languages
for code, st in sorted(lang_metrics.items()):
    if code == "en": continue
    tot_q += st["total_queries"]
    tot_gt += st["gt_queries"]
    tot_h1 += st["hits1_full"]
    tot_h3 += st["hits3_full"]
    tot_h5 += st["hits5_full"]
    r1 = (st["hits1_full"] / st["total_queries"]) * 100.0
    r3 = (st["hits3_full"] / st["total_queries"]) * 100.0
    r5 = (st["hits5_full"] / st["total_queries"]) * 100.0
    fr5 = (st["hits5_full"] / st["gt_queries"]) * 100.0 if st["gt_queries"] > 0 else 0.0
    print(f"{'Target Language':<16} | {st['name']:<12} | {code:<8} | {st['total_queries']:<5} | {st['gt_queries']:<4} | {st['hits1_full']:<4} | {st['hits3_full']:<4} | {st['hits5_full']:<4} | {r1:>7.1f}% | {r3:>7.1f}% | {r5:>7.1f}% | {fr5:>9.1f}%")

print("=" * 110)
print(f"OVERALL TOTALS:")
print(f"  Total Queries Evaluated               : {tot_q}")
print(f"  Queries with Ground Truth (is_sel=1) : {tot_gt} (Present in FAISS index: {tot_gt})")
print(f"  Queries without Ground Truth         : {tot_q - tot_gt}")
print(f"  Total Hits@1                          : {tot_h1}")
print(f"  Total Hits@3                          : {tot_h3}")
print(f"  Total Hits@5                          : {tot_h5}")
print(f"  Full Dataset Recall@1 (All {tot_q} queries)   : {tot_h1}/{tot_q} = {(tot_h1/tot_q)*100.0:.2f}%")
print(f"  Full Dataset Recall@3 (All {tot_q} queries)   : {tot_h3}/{tot_q} = {(tot_h3/tot_q)*100.0:.2f}%")
print(f"  Full Dataset Recall@5 (All {tot_q} queries)   : {tot_h5}/{tot_q} = {(tot_h5/tot_q)*100.0:.2f}%")
print(f"  Filtered GT Recall@1  (GT {tot_gt} queries)  : {tot_h1}/{tot_gt} = {(tot_h1/tot_gt)*100.0:.2f}%")
print(f"  Filtered GT Recall@3  (GT {tot_gt} queries)  : {tot_h3}/{tot_gt} = {(tot_h3/tot_gt)*100.0:.2f}%")
print(f"  Filtered GT Recall@5  (GT {tot_gt} queries)  : {tot_h5}/{tot_gt} = {(tot_h5/tot_gt)*100.0:.2f}%")
