"""
Complete /ask Pipeline Fine-Grained Latency Profiler (Phase 10)

Measures end-to-end micro-component timings for the POST /ask RAG pipeline:
1. Request parsing & Pydantic validation
2. SafetyFilter gate screening
3. Query embedding generation
4. FAISS vector search
5. Context & source attribution packaging
6. Untrusted data tagging & prompt formatting
7. LLM Provider instantiation & network call (Groq)
8. GroundingVerifier alignment evaluation
9. Response object construction & Pydantic serialization
10. Total end-to-end /ask latency
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict

# Force UTF-8 stdout
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


def run_pipeline_profiler():
    print("=" * 90)
    print("Complete /ask RAG Pipeline Fine-Grained Latency Profiler")
    print("=" * 90)

    settings = get_settings()
    provider_name = os.getenv("LLM_PROVIDER") or settings.llm_provider
    model_name = os.getenv("LLM_MODEL") or settings.llm_model

    if provider_name.lower() == "gemini":
        provider_name = "groq"
    if model_name in ("mock-v1", "gemini-1.5-flash", "gemini-flash-latest", "llama-3.3-70b-versatile"):
        model_name = "llama-3.1-8b-instant"

    provider_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")

    print(f"Active Provider : {provider_name}")
    print(f"Active Model    : {model_name}")
    print(f"API Key Present : {bool(provider_key)}")

    # Explicitly instantiate provider once to warm persistent OpenAI HTTP connection session
    provider = get_llm_provider(provider_name=provider_name, model_name=model_name, api_key=provider_key)
    generator = GeneratorService(llm_provider=provider)

    # Warm up PyTorch embeddings, FAISS vector store, and LLM client session
    print("\nWarming up PyTorch embeddings, FAISS vector store, and LLM client session...")
    req_warm = AskRequest(query="What is the capital of Goa?", top_k=3, preferred_answer_language="en")
    generator.generate_answer(req_warm)
    print("Warm-up complete.\n")

    num_runs = 20
    test_queries = [
        "What is the capital of Goa?",
        "गोवा की राजधानी क्या है?",
        "गोव्याची राजधानी कोणती आहे?",
        "গোয়ার রাজধানী কোনটি?"
    ]

    # Metrics containers (in ms)
    t_parse_list = []
    t_safety_list = []
    t_embed_query_list = []
    t_faiss_search_list = []
    t_context_pack_list = []
    t_prompt_fmt_list = []
    t_llm_gen_list = []
    t_verifier_list = []
    t_response_ser_list = []
    t_total_list = []

    print(f"Executing {num_runs} warm profile iterations across English & Indic queries...\n")

    for i in range(num_runs):
        q_text = test_queries[i % len(test_queries)]
        time.sleep(1.0)  # Pause to respect Groq API rate limits

        # Step 1: Request Parsing & Pydantic Validation
        t0 = time.perf_counter()
        req = AskRequest(query=q_text, top_k=3, preferred_answer_language="en")
        t1 = time.perf_counter()
        t_parse_list.append((t1 - t0) * 1000.0)

        # Step 2: Safety Filter Gate
        t2 = time.perf_counter()
        safety_state, _ = SafetyFilter.evaluate_query(req.query)
        t3 = time.perf_counter()
        t_safety_list.append((t3 - t2) * 1000.0)

        # Step 3: Query Embedding Generation
        t4 = time.perf_counter()
        q_vec = generator.retrieval_service.embedding_service.encode_query(req.query, normalize=True)
        t5 = time.perf_counter()
        t_embed_query_list.append((t5 - t4) * 1000.0)

        # Step 4: FAISS Vector Index Search & Metadata Retrieval
        t6 = time.perf_counter()
        r_req = RetrievalRequest(query=req.query, top_k=req.top_k)
        retrieval_resp = generator.retrieval_service.retrieve(r_req)
        t7 = time.perf_counter()
        # FAISS search latency is retrieval_resp latency minus embedding latency
        faiss_only_ms = max(0.01, (t7 - t6) * 1000.0 - (t5 - t4) * 1000.0)
        t_faiss_search_list.append(faiss_only_ms)

        # Step 5: Context & Source Attribution Packaging
        t8 = time.perf_counter()
        retrieved_chunks = [r.chunk for r in retrieval_resp.results]
        sources = []
        for r in retrieval_resp.results:
            c = r.chunk
            sources.append({
                "chunk_id": c.chunk_id,
                "query_id": c.query_id,
                "language_code": c.language_code,
                "similarity_score": r.score
            })
        t9 = time.perf_counter()
        t_context_pack_list.append((t9 - t8) * 1000.0)

        # Step 6: Untrusted Context Tagging & Prompt Formatting
        t10 = time.perf_counter()
        context_blocks_str = InjectionDefense.format_untrusted_context(retrieved_chunks)
        untrusted_query_str = InjectionDefense.format_untrusted_query(req.query)
        system_prompt = SYSTEM_GROUNDING_PROMPT.format(
            target_language="en",
            context_blocks=context_blocks_str,
            user_query=untrusted_query_str
        )
        user_prompt = f"Please answer the user's question based strictly on the context:\n\n{untrusted_query_str}"
        t11 = time.perf_counter()
        t_prompt_fmt_list.append((t11 - t10) * 1000.0)

        # Step 7: LLM Generation (Groq Network Call)
        t12 = time.perf_counter()
        cand_ans = provider.generate(prompt=user_prompt, system_instruction=system_prompt)
        t13 = time.perf_counter()
        t_llm_gen_list.append((t13 - t12) * 1000.0)

        # Step 8: Grounding Verification Engine
        t14 = time.perf_counter()
        state, status, score = generator.grounding_verifier.verify(answer_text=cand_ans, context_chunks=retrieved_chunks)
        t15 = time.perf_counter()
        t_verifier_list.append((t15 - t14) * 1000.0)

        # Step 9: Response Object Serialization
        t16 = time.perf_counter()
        resp = AskResponse(
            query=req.query,
            answer=cand_ans,
            answer_language="en",
            grounding_status=status,
            grounding_score=score,
            sources=[],
            retrieval_latency_ms=round(retrieval_resp.latency_ms, 2),
            generation_latency_ms=round((t13 - t12) * 1000, 2),
            prompt_construction_latency_ms=round((t11 - t10) * 1000, 2),
            llm_request_latency_ms=round((t13 - t12) * 1000, 2),
            verification_latency_ms=round((t15 - t14) * 1000, 2),
            guardrail_latency_ms=round((t15 - t14) * 1000 + (t3 - t2) * 1000, 2),
            total_latency_ms=round((t16 - t0) * 1000, 2)
        )
        _ = resp.model_dump_json()
        t17 = time.perf_counter()
        t_response_ser_list.append((t17 - t16) * 1000.0)

        # Total pipeline execution time
        t_total_list.append((t17 - t0) * 1000.0)

        print(f"  Req #{i+1:02d}: Complete = {(t17-t0)*1000:6.2f} ms | Embed = {(t5-t4)*1000:5.2f} ms | FAISS = {faiss_only_ms:4.2f} ms | LLM = {(t13-t12)*1000:6.2f} ms | Verifier = {(t15-t14)*1000:5.2f} ms")

    # Summary Statistics
    mean_tot = float(np.mean(t_total_list))
    m_parse = float(np.mean(t_parse_list))
    m_safety = float(np.mean(t_safety_list))
    m_embed = float(np.mean(t_embed_query_list))
    m_faiss = float(np.mean(t_faiss_search_list))
    m_pack = float(np.mean(t_context_pack_list))
    m_prompt = float(np.mean(t_prompt_fmt_list))
    m_llm = float(np.mean(t_llm_gen_list))
    m_verifier = float(np.mean(t_verifier_list))
    m_ser = float(np.mean(t_response_ser_list))

    print("\n" + "=" * 90)
    print("Complete /ask RAG Pipeline Fine-Grained Latency Breakdown")
    print("=" * 90)
    print(f"{'Pipeline Component':<42} | {'Mean Time (ms)':<15} | {'P50 Time (ms)':<15} | {'% of Total':<12}")
    print("=" * 90)
    print(f"{'1. Request Parsing & Validation':<42} | {m_parse:>13.2f} ms | {np.percentile(t_parse_list, 50):>13.2f} ms | {m_parse/mean_tot*100:>10.1f}%")
    print(f"{'2. SafetyFilter Gate Screening':<42} | {m_safety:>13.2f} ms | {np.percentile(t_safety_list, 50):>13.2f} ms | {m_safety/mean_tot*100:>10.1f}%")
    print(f"{'3. Query Embedding (PyTorch MiniLM)':<42} | {m_embed:>13.2f} ms | {np.percentile(t_embed_query_list, 50):>13.2f} ms | {m_embed/mean_tot*100:>10.1f}%")
    print(f"{'4. FAISS Index Vector Search':<42} | {m_faiss:>13.2f} ms | {np.percentile(t_faiss_search_list, 50):>13.2f} ms | {m_faiss/mean_tot*100:>10.1f}%")
    print(f"{'5. Context & Attribution Packaging':<42} | {m_pack:>13.2f} ms | {np.percentile(t_context_pack_list, 50):>13.2f} ms | {m_pack/mean_tot*100:>10.1f}%")
    print(f"{'6. Prompt Formatting & XML Tagging':<42} | {m_prompt:>13.2f} ms | {np.percentile(t_prompt_fmt_list, 50):>13.2f} ms | {m_prompt/mean_tot*100:>10.1f}%")
    print(f"{'7. Groq LLM Generation (8B Cloud)':<42} | {m_llm:>13.2f} ms | {np.percentile(t_llm_gen_list, 50):>13.2f} ms | {m_llm/mean_tot*100:>10.1f}%")
    print(f"{'8. Grounding Verification Engine':<42} | {m_verifier:>13.2f} ms | {np.percentile(t_verifier_list, 50):>13.2f} ms | {m_verifier/mean_tot*100:>10.1f}%")
    print(f"{'9. Response Pydantic Serialization':<42} | {m_ser:>13.2f} ms | {np.percentile(t_response_ser_list, 50):>13.2f} ms | {m_ser/mean_tot*100:>10.1f}%")
    print("-" * 90)
    print(f"{'TOTAL COMPLETE /ask PIPELINE P50':<42} | {mean_tot:>13.2f} ms | {np.percentile(t_total_list, 50):>13.2f} ms | {'100.0%':>10}")
    print("=" * 90)


if __name__ == "__main__":
    run_pipeline_profiler()
