"""
CLI Test Script for Multilingual Retrieval Service (Phase 6)

Executes test queries across English and Indic target languages against the 3,993-vector FAISS index
and displays top-k retrieved chunks, similarity scores, metadata provenance, and latency breakdowns.
"""

import os
import sys

# Force UTF-8 encoding for standard output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to python path for importing app packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.retrieval import RetrievalRequest
from app.rag.retrieval import RetrievalService

TEST_QUERIES = [
    # 1. English Query
    {"query": "What is the capital of Goa?", "lang": None, "top_k": 3},
    # 2. Hindi Query
    {"query": "गोवा की राजधानी क्या है?", "lang": "hi", "top_k": 3},
    # 3. Marathi Query
    {"query": "गोव्याची राजधानी कोणती आहे?", "lang": "mr", "top_k": 3},
    # 4. Bengali Query
    {"query": "গোয়ার রাজধানী কী?", "lang": "bn", "top_k": 3},
    # 5. Tamil Query
    {"query": "கோவாவின் தலைநகரம் எது?", "lang": "ta", "top_k": 3},
    # 6. Telugu Query
    {"query": "గోవా రాజధాని ఏది?", "lang": "te", "top_k": 3},
    # 7. Urdu Query
    {"query": "گوا کا دارالحکومت کون سا ہے؟", "lang": "ur", "top_k": 3},
]


def run_retrieval_cli():
    print("=" * 70)
    print("Phase 6 — Multilingual Retrieval Service CLI Test")
    print("=" * 70)

    service = RetrievalService()

    for idx, tq in enumerate(TEST_QUERIES, 1):
        q_str = tq["query"]
        l_filter = tq["lang"]
        k = tq["top_k"]

        print(f"\n[{idx}/{len(TEST_QUERIES)}] Query: '{q_str}' (Filter: {l_filter or 'None'}, Top-K: {k})")

        req = RetrievalRequest(query=q_str, top_k=k, language_filter=l_filter)
        resp = service.retrieve(req)

        print(f"  Total Latency : {resp.latency_ms:.2f} ms")
        print(f"  Breakdown     : Embed: {resp.latency_breakdown['query_embedding_ms']:.2f}ms | FAISS: {resp.latency_breakdown['faiss_search_ms']:.2f}ms | Meta: {resp.latency_breakdown['metadata_lookup_ms']:.2f}ms")
        print(f"  Results Count : {resp.total_results}")

        for res in resp.results:
            c = res.chunk
            print(f"    Rank {res.rank} | Score: {res.score:.4f} | Lang: {c.language_name} ({c.language_code}) | Chunk ID: {c.chunk_id}")
            print(f"      Text: {c.text[:90]}...")

        # Display LLM Context preview
        llm_context = resp.format_context_for_llm()
        print(f"  Formatted LLM Context Length: {len(llm_context)} chars")

    print("\n" + "=" * 70)
    print("CLI Retrieval Verification Complete")
    print("=" * 70)


if __name__ == "__main__":
    run_retrieval_cli()
