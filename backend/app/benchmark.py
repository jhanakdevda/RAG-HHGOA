"""
RAGE HH GOA — Multilingual Retrieval Latency Benchmark

Measures real end-to-end vector retrieval latency (Embedding + FAISS Search)
against the 50 ms target using the production RetrievalService.

Usage:
    python -m app.benchmark [n_queries]
"""

import sys
import time
import statistics
from typing import List, Dict, Any

from app.models.retrieval import RetrievalRequest
from app.rag.retrieval import RetrievalService

LATENCY_BUDGET_MS = 50.0

MULTILINGUAL_QUERIES = [
    # English
    {"lang": "English", "query": "What is a corporation and how does it function?"},
    {"lang": "English", "query": "What are the primary causes of climate change?"},
    {"lang": "English", "query": "How does cellular respiration generate ATP in organisms?"},
    {"lang": "English", "query": "What is the function of the human heart in blood circulation?"},
    {"lang": "English", "query": "What are renewable energy sources and their benefits?"},
    {"lang": "English", "query": "How does photosynthesis work in green plants?"},
    {"lang": "English", "query": "What is the role of government in economic stability?"},
    {"lang": "English", "query": "What causes ocean currents and how do they affect weather?"},
    {"lang": "English", "query": "How are vaccines developed and tested for safety?"},
    {"lang": "English", "query": "What is the difference between speed and velocity in physics?"},

    # Hindi
    {"lang": "Hindi", "query": "पर्यावरण संरक्षण क्यों महत्वपूर्ण है?"},
    {"lang": "Hindi", "query": "भारतीय संविधान की मुख्य विशेषताएं क्या हैं?"},
    {"lang": "Hindi", "query": "मानव शरीर में जल का क्या महत्व है?"},
    {"lang": "Hindi", "query": "सौर ऊर्जा के क्या लाभ हैं?"},
    {"lang": "Hindi", "query": "कंप्यूटर नेटवर्क क्या है और यह कैसे काम करता है?"},
    {"lang": "Hindi", "query": "सतत विकास का क्या अर्थ है?"},
    {"lang": "Hindi", "query": "वायु प्रदूषण को कम करने के उपाय क्या हैं?"},
    {"lang": "Hindi", "query": "डिजिटल अर्थव्यवस्था क्या है?"},
    {"lang": "Hindi", "query": "पौधों में प्रकाश संश्लेषण प्रक्रिया कैसे होती है?"},
    {"lang": "Hindi", "query": "शिक्षा का अधिकार अधिनियम क्या है?"},

    # Marathi
    {"lang": "Marathi", "query": "पर्यावरण संवर्धनाचे महत्त्व काय आहे?"},
    {"lang": "Marathi", "query": "पाण्याचे मानवी शरीरातील कार्य काय आहे?"},
    {"lang": "Marathi", "query": "सौर ऊर्जेचे फायदे कोणते आहेत?"},
    {"lang": "Marathi", "query": "संगणक नेटवर्क म्हणजे काय आणि ते कसे कार्य करते?"},
    {"lang": "Marathi", "query": "शाश्वत विकास म्हणजे काय?"},
    {"lang": "Marathi", "query": "हवा प्रदूषण कमी करण्याचे उपाय कोणते?"},
    {"lang": "Marathi", "query": "डिजिटल अर्थव्यवस्था म्हणजे काय?"},
    {"lang": "Marathi", "query": "वनस्पतींमधील प्रकाशसंश्लेषण प्रक्रिया कशी होते?"},
    {"lang": "Marathi", "query": "आरोग्यासाठी संतुलित आहाराचे महत्त्व काय?"},
    {"lang": "Marathi", "query": "भारतीय संविधानाची प्रमुख वैशिष्ट्ये कोणती?"},

    # Bengali
    {"lang": "Bengali", "query": "পরিবেশ সংরক্ষণের গুরুত্ব কী?"},
    {"lang": "Bengali", "query": "মানবদেহে জলের ভূমিকা কী?"},
    {"lang": "Bengali", "query": "সৌর শক্তির প্রধান সুবিধাগুলি কী কী?"},
    {"lang": "Bengali", "query": "কম্পিউটার নেটওয়ার্ক কীভাবে কাজ করে?"},
    {"lang": "Bengali", "query": "টেকসই উন্নয়ন বলতে কী বোঝায়?"},
    {"lang": "Bengali", "query": "বায়ু দূষণ নিয়ন্ত্রণের উপায়গুলি কী কী?"},
    {"lang": "Bengali", "query": "ডিজিটাল অর্থনীতি বলতে কী বোঝায়?"},
    {"lang": "Bengali", "query": "উদ্ভিদে সালোকসংশ্লেষ প্রক্রিয়া কীভাবে ঘটে?"},
    {"lang": "Bengali", "query": "সুষম খাদ্যের স্বাস্থ্যগত সুবিধা কী?"},
    {"lang": "Bengali", "query": "ভারতীয় সংবিধানের মূল বৈশিষ্ট্যগুলি কী?"},

    # Telugu
    {"lang": "Telugu", "query": "పర్యావరణ పరిరక్షణ యొక్క ప్రాముఖ్యత ఏమిటి?"},
    {"lang": "Telugu", "query": "మానవ శరీరంలో నీటి పాత్ర ఏమిటి?"},
    {"lang": "Telugu", "query": "సౌర శక్తి యొక్క ప్రయోజనాలు ఏమిటి?"},
    {"lang": "Telugu", "query": "కంప్యూటర్ నెట్‌వర్క్ ఎలా పనిచేస్తుంది?"},
    {"lang": "Telugu", "query": "సుస్థిర అభివృద్ధి అంటే ఏమిటి?"},
    {"lang": "Telugu", "query": "గాలి కాలుష్యాన్ని నివారించే మార్గాలు ఏమిటి?"},
    {"lang": "Telugu", "query": "డిజిటల్ ఆర్థిక వ్యవస్థ అంటే ఏమిటి?"},
    {"lang": "Telugu", "query": "మొక్కలలో కిరణజన్య సంయోగ క్రియ ఎలా జరుగుతుంది?"},
    {"lang": "Telugu", "query": "సమతుల్య ఆహారం యొక్క ఉపయోగాలు ఏమిటి?"},
    {"lang": "Telugu", "query": "భారత రాజ్యాంగం యొక్క ముఖ్య లక్షణాలు ఏమిటి?"},
]


def percentile(values: List[float], pct: float) -> float:
    """Calculates linear interpolation percentile for measured latency values."""
    if not values:
        return 0.0
    s_vals = sorted(values)
    k = (len(s_vals) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(s_vals) - 1)
    if f == c:
        return s_vals[f]
    return s_vals[f] + (k - f) * (s_vals[c] - s_vals[f])


def main():
    n_queries = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    print("Initializing production RetrievalService...")
    try:
        service = RetrievalService()
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to instantiate RetrievalService: {e}")
        sys.exit(1)

    print("Warming up (model load + FAISS index initialization)...")
    try:
        w_start = time.perf_counter()
        warmup_req = RetrievalRequest(query="Warmup query initialization", top_k=5)
        w_resp = service.retrieve(warmup_req)
        w_total_ms = (time.perf_counter() - w_start) * 1000.0
        w_embed_ms = w_resp.latency_breakdown.get("query_embedding_ms", 0.0)
        w_search_ms = w_resp.latency_breakdown.get("faiss_search_ms", 0.0)

        print(f"Cold-start / Warmup retrieval latency: {w_total_ms:.2f} ms (embed: {w_embed_ms:.2f} ms, search: {w_search_ms:.2f} ms)")
        print("Warmup complete. Cold-start latency excluded from steady-state measurements.\n")
    except Exception as e:
        print(f"CRITICAL ERROR during warmup: {e}")
        sys.exit(1)

    # Expose actual production metadata
    model_name = service.embedding_service.model_name
    dimension = service.embedding_service.dimension
    ntotal_vectors = service.vector_store.ntotal

    embed_ms: List[float] = []
    search_ms: List[float] = []
    total_ms: List[float] = []

    # Store per-language latency metrics
    lang_metrics: Dict[str, List[float]] = {
        "English": [],
        "Hindi": [],
        "Marathi": [],
        "Bengali": [],
        "Telugu": []
    }

    top_k = 5

    for i in range(n_queries):
        q_item = MULTILINGUAL_QUERIES[i % len(MULTILINGUAL_QUERIES)]
        query_text = q_item["query"]
        lang_name = q_item["lang"]

        req = RetrievalRequest(query=query_text, top_k=top_k)

        t0 = time.perf_counter()
        resp = service.retrieve(req)
        t1 = time.perf_counter()

        req_total_ms = (t1 - t0) * 1000.0
        req_embed_ms = resp.latency_breakdown.get("query_embedding_ms", 0.0)
        req_search_ms = resp.latency_breakdown.get("faiss_search_ms", 0.0)

        embed_ms.append(req_embed_ms)
        search_ms.append(req_search_ms)
        total_ms.append(req_total_ms)

        if lang_name in lang_metrics:
            lang_metrics[lang_name].append(req_total_ms)

    # Format output according to strict benchmark requirement
    print("RAGE HH GOA — RETRIEVAL LATENCY BENCHMARK\n")
    print(f"Queries: {n_queries}")
    print(f"Top-K: {top_k}")
    print(f"Embedding Model: {model_name}")
    print(f"Embedding Dimension: {dimension}")
    print(f"FAISS Vectors: {ntotal_vectors}\n")

    print(
        f"{'stage':<12}"
        f"{'avg':>8}"
        f"{'p50':>8}"
        f"{'p95':>8}"
        f"{'p99':>8}"
        f"{'max':>8}"
    )
    print("-" * 56)

    for name, values in [
        ("embed", embed_ms),
        ("search", search_ms),
        ("total", total_ms),
    ]:
        print(
            f"{name:<12}"
            f"{statistics.mean(values):>8.2f}"
            f"{percentile(values, 50):>8.2f}"
            f"{percentile(values, 95):>8.2f}"
            f"{percentile(values, 99):>8.2f}"
            f"{max(values):>8.2f}"
        )

    p95_total = percentile(total_ms, 95)

    print(f"\nLatency budget: {LATENCY_BUDGET_MS:.0f} ms")
    print(f"P95 total: {p95_total:.2f} ms\n")

    if p95_total <= LATENCY_BUDGET_MS:
        print("PASS: P95 retrieval latency is within 50 ms")
    else:
        print("FAIL: P95 retrieval latency exceeds 50 ms")

    print("\nLanguage Breakdown:")
    print(
        f"{'Language':<15}"
        f"{'Requests':>10}"
        f"{'Avg Total':>12}"
        f"{'P50':>10}"
        f"{'P95':>10}"
    )
    print("-" * 57)

    for lang in ["English", "Hindi", "Marathi", "Bengali", "Telugu"]:
        l_vals = lang_metrics.get(lang, [])
        l_reqs = len(l_vals)
        if l_reqs > 0:
            print(
                f"{lang:<15}"
                f"{l_reqs:>10}"
                f"{statistics.mean(l_vals):>12.2f}"
                f"{percentile(l_vals, 50):>10.2f}"
                f"{percentile(l_vals, 95):>10.2f}"
            )
        else:
            print(f"{lang:<15}{0:>10}{0.0:>12.2f}{0.0:>10.2f}{0.0:>10.2f}")

    if p95_total > LATENCY_BUDGET_MS:
        sys.exit(1)


if __name__ == "__main__":
    main()
