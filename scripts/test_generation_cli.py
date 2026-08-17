"""
CLI Test Script for Phase 7 Multilingual LLM Answer Generation

Executes end-to-end RAG Q&A queries across English and Indic languages, printing generated answers,
grounding status, source attributions, and actual measured latencies.
"""

import os
import sys

# Force UTF-8 stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.generation import AskRequest
from app.rag.generator import GeneratorService

TEST_QUESTIONS = [
    # 1. English Question
    {"query": "What is the capital of Goa?", "lang": "en"},
    # 2. Hindi Question
    {"query": "गोवा की राजधानी क्या है?", "lang": "hi"},
    # 3. Marathi Question
    {"query": "गोव्याची राजधानी कोणती आहे?", "lang": "mr"},
    # 4. Bengali Question
    {"query": "গোয়ার রাজধানী কী?", "lang": "bn"},
    # 5. Tamil Question
    {"query": "கோவாவின் தலைநகரம் எது?", "lang": "ta"},
    # 6. Telugu Question
    {"query": "గోవా రాజధాని ఏది?", "lang": "te"},
    # 7. Urdu Question
    {"query": "گوا کا دارالحکومت کون سا ہے؟", "lang": "ur"},
    # 8. Out of context / Unanswerable Question
    {"query": "What is the distance between Moon and Mars in kilometers?", "lang": "en"},
]


def run_generation_cli():
    print("=" * 75)
    print("Phase 7 — Multilingual LLM Answer Generation CLI Test")
    print("=" * 75)

    generator = GeneratorService()

    for idx, tq in enumerate(TEST_QUESTIONS, 1):
        q_text = tq["query"]
        preferred_lang = tq["lang"]

        print(f"\n[{idx}/{len(TEST_QUESTIONS)}] Question: '{q_text}' (Lang: {preferred_lang})")

        req = AskRequest(query=q_text, top_k=3, preferred_answer_language=preferred_lang)
        resp = generator.generate_answer(req)

        print(f"  Grounding Status   : {resp.grounding_status}")
        print(f"  Generated Answer   : {resp.answer}")
        print(f"  Sources Attributed : {len(resp.sources)}")
        for src in resp.sources:
            print(f"    - Chunk ID: {src.chunk_id} | Score: {src.similarity_score:.4f} | Lang: {src.language_name}")

        print(f"  Retrieval Latency  : {resp.retrieval_latency_ms:.2f} ms")
        print(f"  Generation Latency : {resp.generation_latency_ms:.2f} ms")
        print(f"  Total Latency      : {resp.total_latency_ms:.2f} ms")

    print("\n" + "=" * 75)
    print("CLI Answer Generation Verification Complete")
    print("=" * 75)


if __name__ == "__main__":
    run_generation_cli()
