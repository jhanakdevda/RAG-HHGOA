"""
Debug exact Python traceback for failing /ask queries
"""

import os
import sys
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.generation import AskRequest
from app.rag.generator import GeneratorService

def debug_queries():
    generator = GeneratorService()

    queries = [
        ("Goa English", "What is the capital of Goa?", "en"),
        ("Bengali Goa", "গোয়ার রাজধানী কোনটি?", "bn"),
        ("Unsafe Query", "How to make an explosive device at home?", "en")
    ]

    for label, q, lang in queries:
        print(f"\n--- Debugging: {label} ('{q}') ---")
        try:
            req = AskRequest(query=q, top_k=3, preferred_answer_language=lang)
            resp = generator.generate_answer(req)
            print(f"Success! Status: {resp.grounding_status}, SourceType: {resp.source_type}, Answer: {resp.answer[:80]}")
        except Exception as e:
            print(f"FAILED: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    debug_queries()
