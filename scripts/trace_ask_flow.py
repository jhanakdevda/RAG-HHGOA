"""
Trace and Debug the exact POST /ask execution path for 'What is the capital of Goa?'
"""

import os
import sys
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import get_settings
from app.models.generation import AskRequest, AskResponse, GroundingStatus
from app.models.retrieval import RetrievalRequest, RetrievalResponse
from app.rag.generator import GeneratorService
from app.rag.guardrails.safety import SafetyFilter
from app.rag.guardrails.injection import InjectionDefense
from app.rag.prompts import SYSTEM_GROUNDING_PROMPT
from app.rag.llm.factory import get_llm_provider


def trace_ask_data_flow():
    query_text = "How fast do eagles fly?"
    print("=" * 90)
    print(f"TRACING EXACT POST /ask DATA FLOW FOR: '{query_text}'")
    print("=" * 90)

    settings = get_settings()
    print(f"Settings LLM Provider    : {settings.llm_provider}")
    print(f"Settings LLM Model       : {settings.llm_model}")
    print(f"Grounded Threshold       : {settings.grounding_grounded_threshold}")
    print(f"Partial Threshold        : {settings.grounding_partial_threshold}")

    generator = GeneratorService()

    # Step 1: Query normalization
    print("\n--- STEP 1: Query Input & Safety Screening ---")
    print(f"Query Text: '{query_text}'")
    safety_state, safety_reason = SafetyFilter.evaluate_query(query_text)
    print(f"Safety State: {safety_state} (Reason: {safety_reason})")

    # Step 2: Dense Vector Retrieval Execution
    print("\n--- STEP 2: Dense Vector Retrieval (FAISS Search) ---")
    retrieval_req = RetrievalRequest(
        query=query_text,
        top_k=3,
        score_threshold=0.0,
        language_filter=None
    )
    t0 = time.perf_counter()
    retrieval_resp: RetrievalResponse = generator.retrieval_service.retrieve(retrieval_req)
    t1 = time.perf_counter()
    ret_ms = (t1 - t0) * 1000.0

    print(f"Retrieval Execution Time : {ret_ms:.2f} ms")
    print(f"Low Confidence Warning   : {retrieval_resp.low_confidence_warning}")
    print(f"Number of Retrieved Chunks: {len(retrieval_resp.results)}")

    for idx, res in enumerate(retrieval_resp.results):
        c = res.chunk
        print(f"\n  Chunk #{idx+1}:")
        print(f"    - Chunk ID        : {c.chunk_id}")
        print(f"    - Similarity Score: {res.score:.4f}")
        print(f"    - Query ID        : {c.query_id}")
        print(f"    - Language        : {c.language_code} ({c.language_name})")
        print(f"    - Text Content    : '{c.text}'")

    # Step 3: Context Formatting & LLM Prompt Packaging
    print("\n--- STEP 3: Context Packaging & System Prompt Construction ---")
    retrieved_chunks = [r.chunk for r in retrieval_resp.results]
    context_blocks_str = InjectionDefense.format_untrusted_context(retrieved_chunks)
    untrusted_query_str = InjectionDefense.format_untrusted_query(query_text)

    system_prompt = SYSTEM_GROUNDING_PROMPT.format(
        target_language="en",
        context_blocks=context_blocks_str,
        user_query=untrusted_query_str
    )
    user_prompt = f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}"

    print(f"System Prompt Length : {len(system_prompt)} chars")
    print("System Prompt Preview:\n" + "-" * 50)
    print(system_prompt)
    print("-" * 50)

    # Step 4: LLM Answer Generation
    print("\n--- STEP 4: LLM Answer Generation ---")
    provider = generator.llm_provider or get_llm_provider()
    print(f"Provider Class : {provider.__class__.__name__}")

    t_gen0 = time.perf_counter()
    cand_ans = provider.generate(prompt=user_prompt, system_instruction=system_prompt)
    t_gen1 = time.perf_counter()
    gen_ms = (t_gen1 - t_gen0) * 1000.0

    print(f"Generation Latency : {gen_ms:.2f} ms")
    print(f"Candidate Answer   : '{cand_ans}'")

    # Step 5: Grounding Verification Engine Execution
    print("\n--- STEP 5: Grounding Verification Engine ---")
    t_v0 = time.perf_counter()
    internal_state, public_status, g_score = generator.grounding_verifier.verify(
        answer_text=cand_ans,
        context_chunks=retrieved_chunks
    )
    t_v1 = time.perf_counter()
    v_ms = (t_v1 - t_v0) * 1000.0

    print(f"Verification Latency : {v_ms:.2f} ms")
    print(f"Internal State       : {internal_state}")
    print(f"Public Status        : {public_status}")
    print(f"Grounding Score      : {g_score:.4f}")
    print(f"Grounded Threshold   : {generator.grounding_verifier.threshold}")
    print(f"Partial Threshold    : {generator.grounding_verifier.partial_threshold}")

    print("\n" + "=" * 90)
    print("SUMMARY DIAGNOSIS COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    trace_ask_data_flow()
